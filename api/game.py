"""
Vercel Serverless Function for Motocross Game
This is a placeholder for Vercel deployment.
The main game runs locally via motocross_game.py
"""

def handler(request):
    return {
        "statusCode": 200,
        "body": {
            "message": "Motocross Game API",
            "status": "running",
            "instructions": "Run 'python motocross_game.py' locally to play"
        }
    }
