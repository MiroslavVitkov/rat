<?php


require 'Parsedown.php';  # A markdown parser.


$h = date('H');
if( $h < 5 )
{
    $pic = 'res/cyber_rat.png';
}
elseif( $h < 11 )
{
    $pic = 'res/day_rat.png';
}
elseif( $h < 20 )
{
    $pic = 'res/saint_rat.png';
}
else
{
    $pic = 'res/asm_rat.png';
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
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <!-- Chatbox at the top -->
    <!-- <div id="chat"></div> -->
    <!-- <input type="text" id="input" placeholder="Type a message and hit Enter..." autofocus> -->

    <!-- Static content -->
    <img src="<?php echo $pic; ?>" alt="Saint Rat" style="max-width: 100%; height: auto;" />
    <pre><span class="inner-pre" style="font-size: 14px"><?php echo $readme_html; ?></span></pre>

    <!-- Code -->
    <!-- <span><script src="myscript.js"></script></span> -->
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');

        input.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && input.value.trim() !== '') {
                const msg = document.createElement('div');
                msg.textContent = input.value;
                chat.appendChild(msg);
                chat.scrollTop = chat.scrollHeight; // scroll to bottom
                input.value = '';
            }
        });
    </script>

</body>
</html>
