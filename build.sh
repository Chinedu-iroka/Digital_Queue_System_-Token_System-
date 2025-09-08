cat > build.sh << 'EOF'
#!/usr/bin/env bash
# Digital Queue System Build Script
echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed!"
EOF