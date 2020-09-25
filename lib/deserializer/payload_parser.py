import base64
import base64
import zlib
import sunspec.core.device as sdev
import sunspec.core.util as sutil
import sunspec.core.suns as suns
import sys
import datetime
from collections import OrderedDict

version = '20190822'
sunsmod = sys.modules['sunspec.core.suns']


# feed this function the following parameters:
#   - created_at: int, unix seconds (e.g., time.mktime(time.gmtime())
#   - model: sunspec.core.device.model object (e.g., dev.device.models[64207][0])
#   - start: int, the index of the 16-bit word to start at.
#   - length:  int, the number of 16-bit words to pack in. default is the rest of the model
# returns base64 encoded payload for web transport
def suns_to_payload(created_at, model, start=0, length=None, use_binary=False, zip_first=True):
    pbytes = bytearray.fromhex('{:08X}'.format(int(created_at)))
    pbytes.extend(sutil.u16_to_data(model.id))
    pbytes.extend(sutil.u16_to_data(start))

    for block in model.blocks:

        # iterate through all points in the block
        for ptype in block.block_type.points_list:
            # check that this point is within the bounds of the portion of the model we're trying to write
            if ptype.offset < start or length is not None and ptype.offset + ptype.len + block.addr > start + length:
                continue

            # check if this point is in the list of regular points
            if ptype.id in block.points:
                point = block.points.get(ptype.id)
            else:
                point = block.points_sf.get(ptype.id)

            # if the point is still not found, it is probably a pad
            if point is None:
                newbytes = ptype.to_data(ptype.value_default)
            else:
                if point.value_getter() is None:
                    # the value was not set, so write the unimplemented value. special case for string
                    typename = ptype.type
                    if typename != 'string':
                        base_value = getattr(sunsmod, 'SUNS_UNIMPL_' + typename.upper())
                    else:
                        base_value = ''
                    newbytes = ptype.to_data(base_value, ptype.len * 2)
                else:
                    newbytes = ptype.to_data(point.value_base, ptype.len * 2)

            #print(ptype.id + ': ' + ''.join('{:02X} '.format(ord(x)) for x in newbytes) + '(' + str(ptype.data_to(newbytes)) + ')')
            pbytes.extend(newbytes)

    if zip_first:
        payload = zlib.compress(str(pbytes))
    else:
        payload = pbytes

    if not use_binary:
        payload = base64.b64encode(payload)

    return payload


def get_headers(payload_bytes):
    timestamp = sutil.data_to_s32(payload_bytes[0:4])
    model_id = sutil.data_to_u16(payload_bytes[4:6])
    offset = sutil.data_to_u16(payload_bytes[6:8])
    headers = {
        'created_at': timestamp,
        'model_id': model_id,
        'start_offset': offset
    }
    return headers


def get_content(payload_bytes):
    return payload_bytes[8:]


# returns dict of the decoded payload
def payload_to_json(payload, use_binary=False, zip_first=True):

    if not use_binary:
        payload = base64.b64decode(payload)

    if zip_first:
        pbytes = zlib.decompress(payload)
    else:
        pbytes = payload

    headers = get_headers(pbytes)
    timestamp = headers['created_at']  # sutil.data_to_s32(pbytes[0:4])
    model_id = headers['model_id']  # sutil.data_to_u16(pbytes[4:6])
    offset = headers['start_offset']  # sutil.data_to_u16(pbytes[6:8])
    data = get_content(pbytes)
    model = sdev.Model(mid=model_id)
    model.load()
    fixed_block_len = int(model.model_type.fixed_block.len)

    if model.model_type.repeating_block is not None:
        repeating_block_len = int(model.model_type.repeating_block.len)
    else:
        repeating_block_len = 0

    num_regs = len(data) / 2  # number of registers contained in payload

    highest_address = num_regs + offset  # highest register address represented in the payload

    # subtract off the fixed block length to see how many repeating block registers are in the payload
    num_repeat_regs = highest_address - fixed_block_len

    if repeating_block_len > 0 and num_repeat_regs > 0:
        # this model has a repeating block and the payload contains data from it
        num_repeat_instances = int((num_repeat_regs + repeating_block_len - 1) / repeating_block_len)
        new_len = fixed_block_len + num_repeat_instances * repeating_block_len

        # reload the model to generate the repeating block instances
        model = sdev.Model(mid=model_id)
        model.len = new_len
        model.load()
    else:
        # no points in repeating block or no repeating block
        num_repeat_instances = 0

    block_lookup = {}  # key = start address of block, value = block index
    reg_points_list = []
    sf_points_list = []

    for i, block in enumerate(model.blocks):
        block_lookup[block.addr] = i
        reg_points_list.extend(block.points_list)  # add all regular points
        sf_points_list.extend([p for p_id, p in block.points_sf.items()]) # scale factors are in a separate container

    # sort the points list by address
    reg_points_list.sort(key=lambda p: int(p.addr))
    sf_points_list.sort(key=lambda p: int(p.addr))

    # combine the points lists, but put scale factors first so we can scale regular points when we get them
    points_list = sf_points_list + reg_points_list

    # TODO: move the output_dict generation to an outside function so it can be also used by other functions
    output_dict = OrderedDict({
        'created_at':   datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'model_name':   model.model_type.name,
        'model_id':     model_id,
        'update':       OrderedDict({
            'fixed':    OrderedDict()
        })
    })

    if num_repeat_instances:
        # build out the repeating block portion of the output dictionary
        output_dict['update']['repeating'] = OrderedDict()
        for rep in range(1, num_repeat_instances + 1):
            output_dict['update']['repeating'][rep] = OrderedDict()

    # load as many points as we can from the payload
    for p in points_list:
        point_bytelen = (int(p.point_type.len) * 2)

        # calculate where we expect this point to be relative to the beginning of the payload
        byte_offset = (int(p.addr) - offset) * 2

        # check if the point has any part outside the bounds of the payload
        if (byte_offset + point_bytelen) > len(data):
            if p.point_type.type != suns.SUNS_TYPE_SUNSSF:
                # quit the loop. reading this point data from the payload would send us beyond the bytearray bounds
                break
            else:
                continue
        elif byte_offset < 0:
            # the payload data starts after this point's address
            continue

        # extract this point value from the payload
        point_data = data[byte_offset:byte_offset + point_bytelen]

        # special treatement for strings
        if p.point_type.type == 'string':
            if sys.version_info < (3,):
                point_data = str(point_data)

        p.value_base = p.point_type.data_to(point_data)

        if p.point_type.type != suns.SUNS_TYPE_SUNSSF:
            # assign the scale factor value if present
            if p.sf_point is not None and p.sf_point.value_base is not None:
                p.value_sf = int(p.sf_point.value_base)

            if p.value_sf is not None and p.value_sf < 0:
                # scale factor is applied within the value_getter() function
                # round to the right number of sigfigs
                val = round(p.value_getter(), abs(p.value_sf))
            else:
                # no need to round if there's no scale factor or if scale factor is positive
                val = p.value_getter()

            # figure out which block this point is in, so it's put in the right place in the output dictionary
            blocknum = block_lookup.get(p.block.addr)
            if p.point_type.type == 'string':
                unimplemented_value = '\x00'
            else:
                unimplemented_value = getattr(sunsmod, 'SUNS_UNIMPL_' + p.point_type.type.upper())
            if p.value_base != unimplemented_value:
                if blocknum == 0:
                    output_dict['update']['fixed'][p.point_type.id] = val
                else:
                    output_dict['update']['repeating'][blocknum][p.point_type.id] = val

    return output_dict


def suns_to_dict(model, created_at, unit_id=None):

    # output_dict = OrderedDict({
    #     'unit_id':  unit_id,
    #     'created_at':   datetime.datetime.utcfromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S UTC'),
    #     'model_name': model.model_type.name,
    #     'model_id':     model.model_type.id,
    #     'update':       OrderedDict({
    #         'fixed':    OrderedDict()
    #     })
    # })

    output_dict = OrderedDict()
    output_dict['created_at'] = datetime.datetime.utcfromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S UTC')
    if unit_id:
        output_dict['unit_id'] = unit_id
    output_dict['model_name'] = model.model_type.name
    output_dict['model_id'] = model.model_type.id
    output_dict['update'] = OrderedDict({
        'fixed': OrderedDict()
    })
    if len(model.blocks) > 1:
        # subtract off the fixed block length to see how many repeating block registers are in this model instance
        num_repeat_regs = model.len - model.blocks[0].len
        num_repeat_blocks = num_repeat_regs / (model.blocks[-1].len)
        if num_repeat_blocks:
            output_dict['update']['repeating'] = OrderedDict()
            for i in range(1, num_repeat_blocks + 1):
                output_dict['update']['repeating'][i] = OrderedDict()
    else:
        num_repeat_blocks = 0

    for block_num, block in enumerate(model.blocks):
        if block_num > num_repeat_blocks:
            break
        # loop through all points in model and generate output dictionary contents
        for p in block.points_list:
            if p.point_type.type != suns.SUNS_TYPE_SUNSSF:

                if p.value_sf is not None and p.value_sf < 0:
                    # scale factor is applied within the value_getter() function
                    # round to the right number of sigfigs
                    val = round(p.value_getter(), abs(p.value_sf))
                else:
                    # no need to round if there's no scale factor or if scale factor is positive
                    val = p.value_getter()

                # figure out which block this point is in, so it's put in the right place in the output dictionary
                if p.point_type.type == 'string':
                    unimplemented_value = '\x00'
                else:
                    try:
                        unimplemented_value = getattr(sunsmod, 'SUNS_UNIMPL_' + p.point_type.type.upper())
                    except Exception:
                        unimplemented_value = None
                if p.value_base != unimplemented_value and val is not None:
                    if block_num == 0:
                        output_dict['update']['fixed'][p.point_type.id] = val
                    else:
                        output_dict['update']['repeating'][block_num][p.point_type.id] = val
    return output_dict