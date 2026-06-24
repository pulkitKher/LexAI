source venv/Scripts/activate
uvicorn main:app --reload --port 8000

echo "# LexAI" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/pulkitKher/LexAI.git
git push -u origin main