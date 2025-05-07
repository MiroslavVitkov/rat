<?php


require 'Parsedown.php';  # A markdown parser.


$h = date('H');
if( $h > 6 and $h < 20 )
{
    $pic = 'res/Saint_Rat.png';
}
else
{
    $pic = 'res/Saint_Rat.png';
}

$readme = file_get_contents('/opt/rat/README.md');

# As a text file
#$readme_html = nl2br(htmlspecialchars($readme));  # Convert line breaks and escape HTML

# Or as parsed markdown.
$Parsedown = new Parsedown();
$readme_html = $Parsedown->text($readme);  # Convert Markdown to HTML


?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>rat</title>
    <link rel="icon" type="image/png" href="res/icon.png">
</head>
<body>
    <img src="<?php echo $pic; ?>" alt="Saint Rat" style="max-width: 100%; height: auto;" />
    <pre><span class="inner-pre" style="font-size: 14px"><?php echo $readme_html; ?></span></pre>

</body>
</html>
