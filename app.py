from flask import Flask, render_template, abort, request, send_file
from pathlib import Path
import sys, os

root_path = Path(os.environ['FS_ROOT'])
mimetypes = {
    ".webp": "image/webp"
}

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route("/<path:path>")
def filebrowser(path):
    path = Path(root_path, path)   

    if not path.exists():
        abort(404)

    download = 'd' in request.args
    show_hidden = 'sh' in request.args

    if path.is_dir():
        folders = [x.relative_to(root_path) for x in path.iterdir() if x.is_dir() and (not x.name.startswith('.') or show_hidden)]
        files = [x.relative_to(root_path) for x in path.iterdir() if x.is_file() and (not x.name.startswith('.') or show_hidden)]
        folders.sort()
        files.sort()

        return render_template('filebrowser.html', 
            path=path.relative_to(root_path),
            folders=folders, 
            files=files
        )
    else:
        return send_file(
            path, 
            download_name=path.name, 
            as_attachment=True if download else False, 
            mimetype=mimetypes[path.suffix] if path.suffix in mimetypes else None
        )

@app.context_processor
def utility_processor():
    def file_size(path:Path):
        path = Path(root_path, path)
        size = path.stat().st_size
        suffix = 'B'
        if size > 900:
            size /= 1024
            suffix = 'KB'
        if size > 900:
            size /= 1024
            suffix = 'MB'
        if size > 900:
            size /= 1024
            suffix = 'GB'
        return f"{size:.2f} {suffix}" if suffix != 'B' else f'{int(size)} {suffix}'
    def relative(path1, path2):
        return path1.relative_to(path2)
    def join(path1, path2):
        return Path(path1, path2)
    return dict(file_size=file_size, prelative=relative, pjoin=join)

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)