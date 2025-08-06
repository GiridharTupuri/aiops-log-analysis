#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import sys

def serve_webpage(port=8000):
    """
    Serve the anomaly detection webpage on localhost
    """
    # Change to the directory containing the HTML file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if the HTML file exists
    if not os.path.exists("anomaly_results.html"):
        print("❌ Error: anomaly_results.html not found!")
        print("Please run 'python3 web_anomaly_display.py' first to generate the webpage.")
        return
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"🌐 Serving anomaly detection webpage at http://localhost:{port}")
            print(f"📄 Direct link: http://localhost:{port}/anomaly_results.html")
            print("Press Ctrl+C to stop the server")
            
            # Try to open the webpage in browser (optional)
            try:
                webbrowser.open(f"http://localhost:{port}/anomaly_results.html")
            except:
                pass  # Browser opening might fail in some environments
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"python3 serve_webpage.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")
    
    serve_webpage(port)