param(
	[string]$SqlDir,
    [Parameter(Mandatory=$True)]
	[string]$UserName,
    [Parameter(Mandatory=$True)]
	[string]$Password,
    [Parameter(Mandatory=$True)]
	[string]$DbName
)


Get-ChildItem $SqlDir -Filter *.sql | 
Foreach-Object {
    $qualName = $_.FullName
    cmd.exe /c echo "exit;" | sqlplus $UserName/$Password@$DbName @$qualName
    "----------- $qualName completed ------------"
}
