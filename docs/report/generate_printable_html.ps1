$md = Get-Content "docs\report\FINAL_PROJECT_REPORT.md" -Raw

function Convert-MarkdownToHtml {
    param([string]$text)
    
    # Normalize line endings
    $text = $text -replace "\r\n", "`n"
    
    # Code blocks
    $codeBlocks = @()
    $text = [regex]::Replace($text, '```(\w*)\n([\s\S]*?)```', {
        param($m)
        $idx = $codeBlocks.Count
        $lang = $m.Groups[1].Value
        $code = [System.Web.HttpUtility]::HtmlEncode($m.Groups[2].Value)
        $codeBlocks += "<pre class='code-block'><code class='language-$lang'>$code</code></pre>"
        return "<!--CODEBLOCK_$idx-->"
    })
    
    # Process line by line for headers, tables, lists, blockquotes
    $lines = $text -split "`n"
    $htmlLines = @()
    $inTable = $false
    $tableRows = @()
    $inList = $false
    $listType = ""
    
    foreach ($line in $lines) {
        # Check if table row
        if ($line -match '^\s*\|(.+)\|\s*$') {
            if (-not $inTable) {
                $inTable = $true
                $tableRows = @()
            }
            # Skip separator row like |:---|:---|
            if ($line -match '^\s*\|(\s*[:\-]+\s*\|)+\s*$') {
                continue
            }
            $tableRows += $line
            continue
        } else {
            if ($inTable) {
                # Close table
                $htmlLines += "<div class='table-container'><table class='report-table'>"
                for ($r = 0; $r -lt $tableRows.Count; $r++) {
                    $row = $tableRows[$r]
                    $cells = ($row -replace '^\s*\||\s*\|\s*$', '') -split '\|'
                    if ($r -eq 0) {
                        $htmlLines += "<thead><tr>"
                        foreach ($c in $cells) {
                            $cTrim = $c.Trim()
                            $htmlLines += "<th>$cTrim</th>"
                        }
                        $htmlLines += "</tr></thead><tbody>"
                    } else {
                        $htmlLines += "<tr>"
                        foreach ($c in $cells) {
                            $cTrim = $c.Trim()
                            $htmlLines += "<td>$cTrim</td>"
                        }
                        $htmlLines += "</tr>"
                    }
                }
                $htmlLines += "</tbody></table></div>"
                $inTable = $false
                $tableRows = @()
            }
        }
        
        # Lists
        if ($line -match '^\s*[\*\-]\s+(.+)$') {
            if (-not $inList) {
                $inList = $true
                $listType = "ul"
                $htmlLines += "<ul>"
            }
            $item = $matches[1]
            $htmlLines += "<li>$item</li>"
            continue
        } elseif ($line -match '^\s*(\d+)\.\s+(.+)$') {
            if (-not $inList) {
                $inList = $true
                $listType = "ol"
                $htmlLines += "<ol>"
            }
            $item = $matches[2]
            $htmlLines += "<li>$item</li>"
            continue
        } else {
            if ($inList) {
                $htmlLines += "</$listType>"
                $inList = $false
            }
        }
        
        # Headers
        if ($line -match '^(#{1,6})\s+(.+)$') {
            $level = $matches[1].Length
            $hText = $matches[2]
            $pageBreakClass = ""
            if ($level -eq 1 -or ($level -eq 2 -and ($hText -match 'Certificate|Student Declaration|Acknowledgement|Abstract|Table of Contents|List of'))) {
                $pageBreakClass = " page-break-before"
            }
            $htmlLines += "<h$level class='heading-$level$pageBreakClass'>$hText</h$level>"
            continue
        }
        
        # Blockquote / Notes
        if ($line -match '^>\s*(.+)$') {
            $quote = $matches[1]
            $htmlLines += "<blockquote class='report-quote'>$quote</blockquote>"
            continue
        }
        
        # Images: ![alt](src)
        if ($line -match '!\[(.*?)\]\((.*?)\)') {
            $alt = $matches[1]
            $src = $matches[2]
            $htmlLines += "<div class='figure-container'><img src='$src' alt='$alt' class='report-figure'/><p class='figure-caption'>$alt</p></div>"
            continue
        }
        
        # Empty line
        if ([string]::IsNullOrWhiteSpace($line)) {
            $htmlLines += ""
            continue
        }
        
        # HTML tags pass-through (like page breaks or br)
        if ($line -match '^\s*<div.*?>.*</div>\s*$' -or $line -match '^\s*<br\s*/?>\s*$') {
            $htmlLines += $line
            continue
        }
        
        # Horizontal rules
        if ($line -match '^\s*---+\s*$') {
            $htmlLines += "<hr class='report-divider'/>"
            continue
        }
        
        # Regular paragraph
        $htmlLines += "<p>$line</p>"
    }
    
    # Close any pending table or list
    if ($inTable) {
        $htmlLines += "<div class='table-container'><table class='report-table'>"
        for ($r = 0; $r -lt $tableRows.Count; $r++) {
            $row = $tableRows[$r]
            $cells = ($row -replace '^\s*\||\s*\|\s*$', '') -split '\|'
            if ($r -eq 0) {
                $htmlLines += "<thead><tr>"
                foreach ($c in $cells) { $htmlLines += "<th>$($c.Trim())</th>" }
                $htmlLines += "</tr></thead><tbody>"
            } else {
                $htmlLines += "<tr>"
                foreach ($c in $cells) { $htmlLines += "<td>$($c.Trim())</td>" }
                $htmlLines += "</tr>"
            }
        }
        $htmlLines += "</tbody></table></div>"
    }
    if ($inList) { $htmlLines += "</$listType>" }
    
    $fullHtml = $htmlLines -join "`n"
    
    # Restore code blocks
    for ($i = 0; $i -lt $codeBlocks.Count; $i++) {
        $fullHtml = $fullHtml.Replace("<!--CODEBLOCK_$i-->", $codeBlocks[$i])
    }
    
    # Inline formatting: Bold **text**, Italic *text*, inline code `code`
    $fullHtml = [regex]::Replace($fullHtml, '\*\*(.+?)\*\*', '<strong>$1</strong>')
    $fullHtml = [regex]::Replace($fullHtml, '(?<!\*)\*([^\*]+?)\*(?!\*)', '<em>$1</em>')
    $fullHtml = [regex]::Replace($fullHtml, '`([^`]+?)`', '<code class="inline-code">$1</code>')
    
    return $fullHtml
}

# Require System.Web for HtmlEncode
Add-Type -AssemblyName System.Web
$bodyContent = Convert-MarkdownToHtml $md

$template = @"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MST vs K-Means Robustness Analysis - Academic Report</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 18mm 15mm 20mm 15mm;
      @bottom-right {
        content: counter(page);
      }
    }
    body {
      font-family: 'Times New Roman', Times, Georgia, serif;
      font-size: 11pt;
      line-height: 1.5;
      color: #1a1a1a;
      background: #ffffff;
      margin: 0 auto;
      max-width: 820px;
      padding: 20px;
    }
    h1, h2, h3, h4 {
      font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
      color: #0f172a;
      font-weight: 700;
      line-height: 1.25;
    }
    h1 {
      font-size: 20pt;
      border-bottom: 2px solid #2563eb;
      padding-bottom: 6px;
      margin-top: 30pt;
      margin-bottom: 14pt;
    }
    h2 {
      font-size: 15pt;
      border-bottom: 1px solid #cbd5e1;
      padding-bottom: 4px;
      margin-top: 22pt;
      margin-bottom: 10pt;
    }
    h3 {
      font-size: 12.5pt;
      margin-top: 16pt;
      margin-bottom: 8pt;
      color: #1e3a8a;
    }
    h4 {
      font-size: 11pt;
      margin-top: 12pt;
      margin-bottom: 6pt;
    }
    p {
      margin-top: 0;
      margin-bottom: 8pt;
      text-align: justify;
      text-justify: inter-word;
    }
    .page-break-before {
      page-break-before: always;
      break-before: page;
    }
    .page-break-after {
      page-break-after: always;
      break-after: page;
    }
    ul, ol {
      margin-top: 0;
      margin-bottom: 10pt;
      padding-left: 24pt;
    }
    li {
      margin-bottom: 3pt;
    }
    /* Tables */
    .table-container {
      width: 100%;
      overflow-x: auto;
      margin: 14pt 0;
      page-break-inside: avoid;
    }
    table.report-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 9.5pt;
      line-height: 1.35;
      border: 1px solid #cbd5e1;
    }
    table.report-table th, table.report-table td {
      border: 1px solid #cbd5e1;
      padding: 6pt 8pt;
      text-align: left;
    }
    table.report-table th {
      background-color: #f1f5f9;
      color: #0f172a;
      font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
      font-weight: 700;
    }
    table.report-table tbody tr:nth-child(even) {
      background-color: #f8fafc;
    }
    /* Figures */
    .figure-container {
      text-align: center;
      margin: 16pt 0;
      page-break-inside: avoid;
    }
    img.report-figure {
      max-width: 95%;
      height: auto;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    p.figure-caption {
      font-size: 9.5pt;
      font-style: italic;
      color: #475569;
      margin-top: 6pt;
      text-align: center;
    }
    /* Code */
    pre.code-block {
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #2563eb;
      padding: 8pt 10pt;
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 8.5pt;
      line-height: 1.4;
      overflow-x: auto;
      margin: 10pt 0;
      page-break-inside: avoid;
    }
    code.inline-code {
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 9pt;
      background: #f1f5f9;
      padding: 1pt 3pt;
      border-radius: 2px;
      border: 1px solid #e2e8f0;
    }
    blockquote.report-quote {
      border-left: 3px solid #3b82f6;
      background: #eff6ff;
      padding: 6pt 10pt;
      margin: 10pt 0;
      font-style: italic;
    }
    hr.report-divider {
      border: none;
      border-top: 1px solid #e2e8f0;
      margin: 16pt 0;
    }
    @media print {
      body {
        max-width: 100%;
        padding: 0;
      }
      .page-break-before {
        page-break-before: always !important;
      }
    }
  </style>
</head>
<body>
$bodyContent
</body>
</html>
"@

$template | Set-Content "docs\report\report_printable.html" -Encoding UTF8
Write-Host "Generated docs\report\report_printable.html successfully!"
