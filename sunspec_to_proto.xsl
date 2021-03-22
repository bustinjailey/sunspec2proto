<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fn="http://www.w3.org/1999/xpath-functions">
    <xsl:output method="text" indent="yes"/>
    <xsl:variable name="newline"><xsl:text>
</xsl:text></xsl:variable>
    <xsl:function name="fn:toPascal">
        <xsl:param name="string"/>
        <xsl:value-of select="string-join(for $s in tokenize($string,'\W+') return concat(upper-case(substring($s,1,1)),substring($s,2)),'')"/>
    </xsl:function>
    <xsl:function name="fn:toProtobufType">
        <xsl:param name="sunspecType"/>
        <xsl:choose>
            <xsl:when test="$sunspecType = 'sunssf'">replaceme</xsl:when>
            <xsl:when test="$sunspecType = 'bitfield16'">map&lt;string, bool&gt;</xsl:when>
            <xsl:otherwise><xsl:value-of select="$sunspecType"/></xsl:otherwise>
        </xsl:choose>
    </xsl:function>
    
    <xsl:template match="/sunSpecModels">
        <xsl:for-each select="model">
            <xsl:variable name="modelId" select="@id"/>
// Model <xsl:value-of select="$modelId"/>: <xsl:value-of select="../strings[@id=current()/@id]/model/label"/>
// Description: <xsl:value-of select="../strings[@id=current()/@id]/model/description"/>
// Notes: <xsl:value-of select="../strings[@id=current()/@id]/model/notes"/> (TODO: Hide if no notes)
message <xsl:value-of select="fn:toPascal(@name)" /> {
            <xsl:for-each select="block/point">
    // <xsl:value-of select="/sunSpecModels/strings[@id=$modelId]/point[@id=current()/@id]/description" />
    optional <xsl:value-of select="fn:toProtobufType(@type)" /><xsl:text> </xsl:text><xsl:value-of select="@id" /> = <xsl:value-of select="@offset"/>;
            </xsl:for-each>
}
            <xsl:value-of select="$newline" />
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
