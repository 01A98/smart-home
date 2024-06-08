from glob import glob
import asyncio


def get_js_file(ts_filepath: str):
    if ts_filepath:
        js_glob_path = "public" + "/" + ts_filepath.replace(".ts", ".*.js")
        return glob(js_glob_path)[0]
    raise ValueError("Must provide ts_filepath relative to templates/views directory")


async def run_command(*args):
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args,
        # stdout must be a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout
    return stdout.decode().strip()
