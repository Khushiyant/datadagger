# DataDagger v2.0 - Post-Twitter API Update

## 🚀 What's New in v2.0

DataDagger has been completely updated to address the **Twitter API changes of February 2023**. We've pivoted to focus on **free and accessible platforms** while maintaining enterprise-grade capabilities.

### ⚡ Key Updates

1. **🆓 Free-First Approach**: Now defaults to Reddit + Mastodon (both FREE)
2. **💰 Twitter Reality Check**: Clear pricing info ($100+/month)
3. **🐘 Mastodon Integration**: Full support for the Twitter alternative
4. **🧙‍♂️ Setup Wizard**: Interactive setup for free platforms
5. **💵 Cost Calculator**: Compare platform costs and features
6. **🎭 Enhanced Demo**: Works without any API keys

## 📊 Platform Support Matrix

| Platform | Status | Cost | API Limits | Best For |
|----------|--------|------|------------|----------|
| **Reddit** | ✅ Full Support | FREE | 60 req/min | Forums, long discussions |
| **Mastodon** | ✅ Full Support | FREE | 300 req/15min | Twitter-like content |
| **Twitter** | ⚠️ Paid Only | $100+/month | 10K tweets/month | Breaking news, trends |

## 🎯 Recommended Workflow

### For Students/Researchers (Budget: $0)
```bash
# 1. Quick start with demo
./datadagger.py demo --show-timeline --show-network

# 2. Set up free APIs
./datadagger.py setup

# 3. Start analyzing
./datadagger.py search "misinformation" --platforms reddit,mastodon
```

### For Organizations (Budget: $1,200/year)
```bash
# Add Twitter for comprehensive coverage
./datadagger.py search "cybersecurity threats" --platforms reddit,mastodon,twitter
./datadagger.py track --query "supply chain attacks" --start-date 2024-01-01 --end-date 2025-01-01
```

## 🆕 New Commands

- `demo` - Interactive demo (no setup required)
- `setup` - Guided API setup wizard  
- `pricing` - Platform cost comparison
- `config` - Enhanced configuration checker

## 📈 Migration from v1.0

If you were using the old version:

1. **Twitter users**: Check `datadagger pricing` for current costs
2. **Free users**: Run `datadagger setup` to configure Reddit + Mastodon
3. **All users**: Try `datadagger demo` to see new features

## 🔮 Future Roadmap

- **Truth Social** API integration
- **Telegram** channel monitoring  
- **LinkedIn** professional networks
- **Academic paper** citation tracking
- **Dark web** forum monitoring (Tor integration)

## 💡 Pro Tips

1. **Start Free**: Reddit + Mastodon covers 85% of social media analysis needs
2. **Academic Access**: Many universities have special Twitter API access
3. **Compliance**: All scrapers respect rate limits and robots.txt
4. **Privacy**: Only public data is collected
5. **Research**: Perfect for threat intelligence and misinformation studies

## 🛡️ Legal & Ethical Use

DataDagger v2.0 is designed for:
- ✅ Security research and threat analysis
- ✅ Academic research on information spread
- ✅ Journalism and fact-checking
- ✅ Brand monitoring and reputation management
- ❌ Harassment or surveillance
- ❌ Violating platform terms of service

## 📞 Support

- 📚 **Documentation**: See README.md and QUICKSTART.md
- 🎮 **Try Demo**: `./datadagger.py demo`
- ⚙️ **Setup Help**: `./datadagger.py setup`
- 💰 **Cost Planning**: `./datadagger.py pricing`

---

**DataDagger v2.0** - Influence Archaeology for the Post-Free-Twitter Era
