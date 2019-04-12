param(
[Parameter(Mandatory=$true)][string]$jarname,
[Parameter(Mandatory=$true)][string]$propsfile,
[Parameter(Mandatory=$true)][string]$propertyname, 
[Parameter(Mandatory=$true)][string]$newvalue
)

function Edit-Properties {
    param([string]$filename, [string]$key, [string]$val)

    $sRawString = Get-Content $filename | Out-String
    $properties = ConvertFrom-StringData $sRawString


    Write-Host "changing ${key} from " $properties."${key}" "to $val"

    # make change
    $properties["${key}"] = "${val}"

    # truncate file
    "" | Out-File -NoNewline -FilePath ${filename} -Encoding utf8

    # write props
    foreach($p in $properties.GetEnumerator()) {
        #escape backslashes
        $p.Value = $p.Value -replace "\\","\\"
        Write-Host $p.Key $p.Value
        "$($p.Key)=$($p.Value)" | Out-File -FilePath ${filename} -Encoding UTF8NoBOM
    }
}

function Extract-Jar-PropsFile {
    param([string]$jarname, [string]$propsfile)
    #extracts the specific file from the .
    jar xf $jarname $propsfile
}

function Update-Jar {
    param([string]$jarname, [string]$addedfile)
    # adds the file to the .jar overwriting any 
    # preexisting file of the same name
    jar uf $jarname $addedfile
}


Extract-Jar-PropsFile $jarname $propsfile
Edit-Properties $propsfile $propertyname $newvalue
Update-Jar $jarname $propsfile

# cleanup
Remove-Item $propsfile
