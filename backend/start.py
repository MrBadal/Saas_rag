"""
Startup script for backend
Ensures proper binding to all interfaces for AWS deployment
"""
import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    # Bind to all interfaces (0.0.0.0) for AWS deployment
    # This allows external access to the backend
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        workers=1
    )
