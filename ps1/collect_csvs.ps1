param(
[string]$searchfilename,
[string]$searchpath, 
[string]$destinationpath
)

#Here's the preliminary script. It takes three parameters:
#1. the name of a zip file you want to look for (in our case `pospoll.zip`) (wildcards are allowed in this param)
#2. The fully qualified path of the location to start the search from (`C:\Oracle`, etc.)
#3. The fully qualified path of the location to put the collected CSVs in 

$searchfiles = Get-ChildItem $searchpath -Filter $searchfilename -Recurse

for ($i=0; $i -lt $searchfiles.Count; $i++) {

    $file = $searchfiles[$i]
    $newfilename = $file.BaseName + $i + $file.Extension
    $filedir = $file.Directory
    $filedestination = $destinationpath + "\" + $newfilename
    Copy-Item $file.FullName -Destination $filedestination
}


$csvsdir = $destinationpath + "\" + "lillii_missing_registers"
mkdir $csvsdir -Force

$zips = Get-ChildItem $destinationpath -Filter pospoll*.zip
for ($i=0; $i -lt $zips.Count; $i++) {
    $zip = $zips[$i]

    $zipbasename = $zip.BaseName
    $normzipbasename = $zipbasename -replace "\."
    $normzipname = $normzipbasename + $zip.Extension
    $expandedzipdir = $destinationpath + "\" + $normzipbasename + "_expanded"
    Expand-Archive $zip.FullName -DestinationPath $expandedzipdir

    echo "expandedzipdir "$expandedzipdir
    $csv = Get-ChildItem $expandedzipdir -Filter missing_packages*.csv
    if (-Not($csv -eq $null) -and -Not(($csv.PSIsContainer))) {
        
        $newcsvname = $csv.BaseName + "-" + $normzipbasename + $csv.Extension

        $csv = Rename-Item -Path $csv.FullName -NewName $newcsvname -PassThru
        Move-Item -Path $csv.FullName -Destination $csvsdir

        Remove-Item -Recurse -Force $expandedzipdir
    }
}
