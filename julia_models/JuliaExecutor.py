import subprocess 
import json 
import os
import tempfile 
import time


class SimpleJuliaExecutor:
    """Simplified Julia executor for .jl files"""

    def __init__(self): 
        self.julia_process = None 
        self.julia_script_path = None 
        self.is_running = False 
        self.start_julia_process()
    def create_julia_script(self):
        """Create Julia communication script""" 
        julia_script = '''
using JSON

function execute_julia_file(file_path) 
    try
        if !isfile(file_path)
            return Dict("success" => false, "error" => "File not found: " * file_path)
        end
        # Capture both stdout and the result 
        old_stdout = stdout
        (rd, wr) = redirect_stdout()

        # Execute the file
        result = include(file_path)

        # Restore stdout and get output 
        redirect_stdout(old_stdout) 
        close(wr)
        output = read(rd, String)
        close(rd)

        return Dict(
            "success" => true,
            "output" => output,
            "result" => isnothing(result) ? "Script completed successfully" :
string(result),
            "file" => basename(file_path)
        )

    catch e
        # Restore stdout if needed 
        try
            redirect_stdout(old_stdout) 
        catch
        end
        return Dict("success" => false, "error" => string(e), "file" => 
basename(file_path))
    end 
end
println("JULIA_READY") 
flush(stdout)
while true
    try
        line = readline()
        if line == "EXIT" || line == "" 
            break
        end
# Execute the file specified in the line 
        result = execute_julia_file(strip(line))
        println("RESULT_START") println(JSON.json(result)) 
        println("RESULT_END") 
        flush(stdout)
    catch e
        println("RESULT_START")
        error_result = Dict("success" => false, "error" => "Communication error: " *
string(e)) 
        println(JSON.json(error_result)) 
        println("RESULT_END") 
        flush(stdout)

    end 
end
'''
        fd, path = tempfile.mkstemp(suffix='.jl', text=True) 
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(julia_script)
            return path
        except:
            os.close(fd) 
            raise

    def start_julia_process(self): 
        """Start Julia process""" 
        try:
            self.julia_script_path = self.create_julia_script()
            self.julia_process = subprocess.Popen([
                'julia', '--startup-file=no', self.julia_script_path
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=0)
            # Wait for ready signal
            start_time = time.time()
            while time.time() - start_time < 20:
                line = self.julia_process.stdout.readline() 
                if line.strip() == "JULIA_READY":
                    self.is_running = True 
                    print("Julia ready for MLJ tasks") 
                    return True
                elif line == "":
                    break
            print("Julia failed to start") 
            self.cleanup()
            return False
        except Exception as e:
            print(f"Failed to start Julia: {e}") 
            self.cleanup()
            return False
    def execute_file(self, file_path, timeout=60): 
        """Execute Julia file"""
        if not self.is_running:
            return {"success": False, "error": "Julia not running"}

        try:
# Send file path 
            self.julia_process.stdin.write(os.path.abspath(file_path) + "\n") 
            self.julia_process.stdin.flush()
# Read result
            return self._read_result(timeout) 
        except Exception as e:
            return {"success": False, "error": f"Execution error: {e}"}

    def _read_result(self, timeout): 
        """Read execution result""" 
        start_time = time.time() 
        result_started = False 
        result_lines = []

        while time.time() - start_time < timeout: 
            try:
                line = self.julia_process.stdout.readline() 
                if line == "":
                    break

                line = line.strip()
                if line == "RESULT_START":
                    result_started = True 
                elif line == "RESULT_END":
                    if result_started and result_lines: 
                        try:
                            return json.loads("\n".join(result_lines)) 
                        except:
                            return {"success": False, "error": "JSON parsing error"} 
                    break
                elif result_started: 
                    result_lines.append(line)
            except:
                break
        return {"success": False, "error": "Execution timeout"}
    def cleanup(self): 
        """Clean up"""
        self.is_running = False
        if self.julia_process and self.julia_process.poll() is None:
            try: 
                self.julia_process.stdin.write("EXIT\n") 
                self.julia_process.stdin.flush() 
                self.julia_process.wait(timeout=3)

            except: 
                self.julia_process.terminate()
        if self.julia_script_path and os.path.exists(self.julia_script_path): 
            try:
                os.unlink(self.julia_script_path) 
            except:
                pass


