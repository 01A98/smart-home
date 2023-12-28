source venv/bin/activate && npm run build && ENV=production npx pm2 start main.py --name smart-home-web-app
