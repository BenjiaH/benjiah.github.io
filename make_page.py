import os
import sys

os.chdir("redirect")
file_name = "{fname}.html".format(fname=sys.argv[2])
f = open(file_name, 'wb')

page_content = '''\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>
            Redirect
        </title>
    </head>
    <body style="background-color:#000000;">
    </body>
    <body>
        <script language="javascript" type="text/javascript">
            var redirect_url = "{redirect_url}";
// console.log(redirect_url);
setTimeout("javascript:location.href=" + "'" + redirect_url + "'", 500);
        </script>
        <h1 align="center">
            <font color="#FFFFFF">
                <font size="7px">
                    Redirecting......
                </font>
            </font>
        </h1>
    </body>

</html>
'''.format(redirect_url=sys.argv[1])
f.write((page_content).encode("utf-8"))
