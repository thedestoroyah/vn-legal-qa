#!/bin/bash
# topdf.sh <in.(pptx|docx|xlsx)> <out.pdf> : render bằng OnlyOffice x2t (máy không có LibreOffice)
F=$HOME/.local/share/onlyoffice/desktopeditors/data/fonts
P=$(mktemp --suffix=.xml)
cat > $P <<X
<?xml version="1.0" encoding="utf-8"?>
<TaskQueueDataConvert xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<m_sFileFrom>$1</m_sFileFrom><m_sFileTo>$2</m_sFileTo><m_nFormatTo>513</m_nFormatTo>
<m_sFontDir>$F</m_sFontDir><m_sAllFontsPath>$F/AllFonts.js</m_sAllFontsPath>
<m_bIsNoBase64>true</m_bIsNoBase64><m_sTempDir>/tmp</m_sTempDir>
</TaskQueueDataConvert>
X
/opt/onlyoffice/desktopeditors/converter/x2t $P; rc=$?; rm -f $P; exit $rc
