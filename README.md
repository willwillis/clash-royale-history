# Clash Royale History

Automated Clash Royale battle analytics published to GitHub Pages, updated hourly via GitHub Actions.

## 🚀 Features

- **Automated Data Collection**: Fetches battle data every hour
- **Beautiful Analytics**: Responsive web interface with card images
- **Deck Performance**: Win rates, trophy changes, usage statistics
- **Battle History**: Recent battles with detailed results
- **Clan Activity**: Member activity tracking and last seen times
- **Mobile Optimized**: Responsive design for all devices

## 📋 Setup Instructions

### 1. Repository Setup

1. **Fork or create a new repository** from this template
2. **Enable GitHub Pages** in repository settings:
   - Go to Settings → Pages
   - Source: "GitHub Actions"

### 2. Secrets Configuration

Add the following secrets in repository settings (Settings → Secrets and variables → Actions):

- `CR_API_TOKEN`: Your Clash Royale API token from [developer.clashroyale.com](https://developer.clashroyale.com)
- `CR_PLAYER_TAG`: Your player tag (e.g., `#YVJR0JLY`)

### 3. Card Images (Optional)

To display card images:

1. Create a `cards/` directory in the repository root
2. Add subdirectories: `cards/normal_cards/` and `cards/evolution_cards/`
3. Place card PNG files using the naming convention (see `html_generator.py` for mappings)

Example structure:
```
cards/
├── normal_cards/
│   ├── Knight.png
│   ├── Wizard.png
│   └── ...
└── evolution_cards/
    ├── Knight.png
    ├── Wizard.png
    └── ...
```

### 4. First Run

The action will run automatically:
- **Hourly**: `0 * * * *` (every hour at minute 0)
- **Manual**: Use "Run workflow" button in Actions tab
- **On push**: When you push to main branch

## 🔄 How It Works

1. **Data Collection**: GitHub Actions runs `analyzer.py` to fetch battle data from Clash Royale API
2. **Database Update**: SQLite database (`clash_royale.db`) is updated and committed back to repo
3. **HTML Generation**: `html_generator.py` creates responsive HTML report
4. **GitHub Pages**: HTML is deployed to GitHub Pages automatically

## 📁 Project Structure

```
clash-royale-history/
├── .github/workflows/
│   └── update-analytics.yml    # GitHub Actions workflow
├── src/
│   ├── analyzer.py            # Data collection and storage
│   └── html_generator.py      # HTML report generation
├── cards/                     # Card images (optional)
├── pyproject.toml            # uv dependencies
└── README.md
```

## 🛠️ Local Development

```bash
# Install dependencies
uv sync

# Set environment variables
export CR_API_TOKEN="your_token_here"
export CR_PLAYER_TAG="#your_tag_here"

# Run data collection
cd src
uv run python analyzer.py

# Generate HTML report
uv run python html_generator.py
```

## 🔐 Security Notes

- API tokens are stored as GitHub Secrets (encrypted)
- Database contains no sensitive information
- All data is publicly visible on GitHub Pages

## 📊 Data Tracked

- **Player Stats**: Trophies, level, clan info, win rate
- **Battle Performance**: Results, trophy changes, crown counts
- **Deck Analytics**: Win rates by deck composition
- **Clan Activity**: Member donations, activity status
- **Historical Trends**: Battle history over time

## 🎨 Responsive Design

The web interface adapts to different screen sizes:
- **Desktop**: Full tables with all data
- **Mobile**: Card-based layouts for easier viewing
- **Touch-friendly**: Optimized for mobile interaction

## 🤝 Contributing

Feel free to submit issues and pull requests to improve the analytics or add new features!

## 📄 License

MIT License - Feel free to use and modify as needed.