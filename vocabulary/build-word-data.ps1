Add-Type -AssemblyName System.Web.Extensions
$serializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$source = Get-Content -Raw -Encoding UTF8 dictionary-source.json
$pattern = '(?ms)^  "([a-z]+(?:-[a-z]+)?)":\s*(\{.*?^  \})(?:,|\s*$)'
$entries = [regex]::Matches($source, $pattern) | ForEach-Object {
  $word = $_.Groups[1].Value
  $data = $serializer.DeserializeObject($_.Groups[2].Value)
  if ($word.Length -gt 1 -and $data['ja'].Count -gt 0) {
    [pscustomobject]@{ Word = $word; Data = $data; Rank = [int]$data['rank'] }
  }
}
$words = $entries | Sort-Object Rank | Select-Object -First 2000 | ForEach-Object {
  $level = if ($_.Data['svl_level']) { [int]$_.Data['svl_level'] } else { 1 }
  $category = if ($level -le 2) { 'BASIC' } elseif ($level -le 5) { 'DAILY' } elseif ($level -le 8) { 'ACADEMIC' } else { 'ADVANCED' }
  [ordered]@{
    word = $_.Word
    meaning = ($_.Data['ja'] | Select-Object -First 3) -join '; '
    category = $category
    level = $level
  }
}
$serializer.MaxJsonLength = 8388608
$json = $serializer.Serialize($words)
Set-Content -Encoding UTF8 words-data.js "window.WORDMARK_WORDS = $json;"
Write-Output "Generated $($words.Count) words."
