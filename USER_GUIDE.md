# 📖 User Guide

Welcome to **DataQuery AI**! This guide will walk you through everything you need to know to start querying your databases using natural language.

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Account Setup](#account-setup)
- [Connecting Your Database](#connecting-your-database)
- [Using the Chat Interface](#using-the-chat-interface)
- [Managing Connections](#managing-connections)
- [Configuring LLM Settings](#configuring-llm-settings)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Getting Started

### What is DataQuery AI?

DataQuery AI is an intelligent platform that lets you interact with your databases using plain English. Instead of writing complex SQL or MongoDB queries, you can simply ask questions like:

- 💬 "Show me all users who signed up last month"
- 💬 "What's our total revenue by product category?"
- 💬 "Find customers who haven't made a purchase in 90 days"

Our AI understands your database structure and generates the appropriate queries automatically!

### Key Features at a Glance

| Feature | What It Does | Icon |
|---------|--------------|------|
| **🔌 Database Connections** | Connect PostgreSQL & MongoDB databases | 🔌 |
| **💬 Natural Language Queries** | Ask questions in plain English | 💬 |
| **🧠 AI-Powered Answers** | Get intelligent, context-aware responses | 🧠 |
| **📊 Query Results** | View data in formatted tables | 📊 |
| **🤖 Multiple LLM Options** | Choose your preferred AI model | 🤖 |
| **📜 Query History** | Review past queries and answers | 📜 |

---

## Account Setup

### Creating Your Account

1. 🌐 Navigate to the application URL (e.g., `http://localhost:3000`)
2. 👋 You'll see the welcome screen with the DataQuery AI logo
3. 📝 Click **"Create Account"** to register
4. 📧 Enter your email address
5. 🔐 Create a secure password (minimum 8 characters recommended)
6. ✅ Click **"Sign Up"**

![Login Screen](https://via.placeholder.com/600x400/4A5568/FFFFFF?text=Login+Screen)

### Logging In

If you already have an account:

1. 📧 Enter your registered email
2. 🔐 Enter your password
3. 🔘 Click **"Sign In"**
4. 🎉 You'll be taken to the Dashboard

### Password Security Tips

- ✅ Use at least 8 characters
- ✅ Include uppercase and lowercase letters
- ✅ Add numbers and special characters
- ❌ Don't reuse passwords from other sites
- ❌ Don't share your credentials

---

## Connecting Your Database

### Supported Databases

| Database | Connection Type | Status |
|----------|----------------|--------|
| 🐘 **PostgreSQL** | Direct connection | ✅ Fully Supported |
| 🍃 **MongoDB** | Atlas or self-hosted | ✅ Fully Supported |

### Step-by-Step Connection Guide

#### 1. Navigate to Connections

From the Dashboard, click the **"Connections"** link in the navigation bar or select **"Connect Database"** from the feature cards.

#### 2. Add a New Connection

Click the **"+ Add Connection"** button to open the connection form.

#### 3. Fill in Connection Details

**For PostgreSQL:**

| Field | Description | Example |
|-------|-------------|---------|
| **Connection Name** | A friendly name for this connection | "Production DB" |
| **Database Type** | Select PostgreSQL | postgresql |
| **Connection String** | Full PostgreSQL connection URL | `postgresql://user:pass@host:5432/dbname` |

**Connection String Format:**
```
postgresql://username:password@hostname:port/database_name
```

**Examples:**
```
# Local PostgreSQL
postgresql://postgres:mypassword@localhost:5432/mydb

# AWS RDS
postgresql://admin:secret@mydb.abc123.us-east-1.rds.amazonaws.com:5432/production

# Heroku
postgresql://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/abc123
```

**For MongoDB:**

| Field | Description | Example |
|-------|-------------|---------|
| **Connection Name** | A friendly name for this connection | "Mongo Atlas" |
| **Database Type** | Select MongoDB | mongodb |
| **Connection String** | Full MongoDB connection URL | `mongodb+srv://user:pass@cluster.mongodb.net/dbname` |

**Connection String Format:**
```
mongodb+srv://username:password@cluster.mongodb.net/database_name
```

**Examples:**
```
# MongoDB Atlas
mongodb+srv://myuser:mypassword@mycluster.abc123.mongodb.net/mydb

# Self-hosted MongoDB
mongodb://admin:secret@localhost:27017/mydb

# With replica set
mongodb://user:pass@host1:27017,host2:27017/mydb?replicaSet=rs0
```

#### 4. Test the Connection

Click **"Test Connection"** to verify:
- ✅ The database is accessible
- ✅ Credentials are correct
- ✅ Schema can be read

#### 5. Save the Connection

If the test is successful, click **"Save Connection"**. The system will:
- 🔒 Securely store your connection details
- 📊 Index your database schema for RAG
- 🧠 Prepare the AI for questions about your data

![Connection Form](https://via.placeholder.com/600x400/4A5568/FFFFFF?text=Connection+Form)

### Connection Management

Once connected, you can:

| Action | How To Do It |
|--------|--------------|
| **View all connections** | Go to the Connections page |
| **Edit a connection** | Click the edit icon (✏️) next to a connection |
| **Delete a connection** | Click the delete icon (🗑️) and confirm |
| **View schema** | Click on a connection name to see its tables/collections |

### Security Notes

- 🔒 Connection strings are encrypted before storage
- 🚫 Passwords are never displayed in the UI
- 🛡️ All database access is read-only by default
- 🔐 Connections are isolated per user account

---

## Using the Chat Interface

The Chat Interface is where the magic happens! This is your natural language query center.

### Accessing the Chat

1. 💬 Click **"Chat"** in the navigation bar
2. 🗄️ Select a database connection from the dropdown
3. 💭 Start typing your question!

### Writing Effective Queries

#### ✅ Good Query Examples

| Question Type | Example | Expected Result |
|--------------|---------|-----------------|
| **Data Retrieval** | "Show me the top 10 customers by revenue" | Sorted list with revenue figures |
| **Aggregation** | "What's the average order value this month?" | Single calculated value |
| **Filtering** | "Find all orders over $1000 from last week" | Filtered order list |
| **Joins** | "List employees with their department names" | Combined data from multiple tables |
| **Time-based** | "How many signups per day last week?" | Time-series data |

#### 💡 Tips for Better Results

1. **Be Specific**
   - ✅ "Show me active users from the United States"
   - ❌ "Show me users"

2. **Use Table/Column Names When Known**
   - ✅ "What's the average price in the products table?"
   - ❌ "What's the average price?"

3. **Specify Time Periods**
   - ✅ "Orders from January 2024"
   - ❌ "Recent orders"

4. **Mention Conditions Clearly**
   - ✅ "Customers who made more than 5 purchases"
   - ❌ "Good customers"

### Understanding Responses

Each AI response typically includes:

#### 1. Natural Language Answer
A human-friendly explanation of the results:
```
The top 5 products by revenue are:
1. Wireless Headphones ($45,230)
2. Smart Watch ($38,900)
3. Laptop Stand ($22,450)
...
```

#### 2. Generated Query (Optional)
The actual SQL or MongoDB query generated:
```sql
SELECT product_name, SUM(price * quantity) as revenue
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 5;
```

#### 3. Result Summary
Information about the query execution:
```
Results: 5 rows returned
Execution time: 0.23 seconds
```

### Chat Features

| Feature | Description | How to Use |
|---------|-------------|------------|
| **Connection Switching** | Change which database you're querying | Use the dropdown at the top |
| **Query History** | See past questions and answers | Scroll up in the chat window |
| **Copy Query** | Copy the generated SQL/MongoDB query | Click the copy icon next to code blocks |
| **Clear Chat** | Start fresh | Click the "Clear" button |

### Example Conversations

#### Example 1: Sales Analysis

**You:** "What's our monthly revenue for the last 6 months?"

**AI:** 
```
Here's the monthly revenue breakdown:

- January 2024: $125,430
- February 2024: $132,890
- March 2024: $118,450
- April 2024: $145,230
- May 2024: $156,780
- June 2024: $149,560

Total: $828,340
Average: $138,057/month

The highest revenue was in May ($156,780) and the lowest was in March ($118,450).
```

**You:** "Which products contributed most to May's revenue?"

**AI:**
```
Top 5 products for May 2024:

1. Enterprise Software License - $45,200 (29%)
2. Consulting Package - $32,100 (20%)
3. Premium Support - $28,500 (18%)
4. Training Sessions - $22,300 (14%)
5. Custom Integration - $18,200 (12%)
```

#### Example 2: Customer Insights

**You:** "Find customers who haven't ordered in the last 90 days"

**AI:**
```
I found 23 customers who haven't placed an order in the last 90 days:

| Customer | Last Order | Total Spent | Email |
|----------|------------|-------------|-------|
| Acme Corp | 2024-01-15 | $12,500 | contact@acme.com |
| TechStart Inc | 2024-01-20 | $8,300 | info@techstart.io |
| ... | ... | ... | ... |

These customers represent $145,600 in historical revenue.
```

---

## Managing Connections

### Viewing All Connections

The Connections page shows:
- 📊 Total number of connections
- 🗄️ Database type icons (PostgreSQL 🐘, MongoDB 🍃)
- ✅ Connection status
- 📅 Last updated timestamp

### Connection Details

Click on any connection to view:
- 📋 **Schema Overview**: Tables (PostgreSQL) or Collections (MongoDB)
- 📊 **Table Statistics**: Row counts, column types
- 🔍 **Sample Data**: Preview of actual data
- ⚙️ **Settings**: Edit or delete the connection

### Organizing Connections

**Naming Conventions:**
- Use descriptive names: "Production PostgreSQL" vs "DB1"
- Include environment: "Staging MongoDB", "Dev PostgreSQL"
- Add purpose: "Analytics DB", "User Data"

**Best Practices:**
- 🏷️ Use consistent naming
- 📝 Add descriptions when feature is available
- 🗂️ Group by environment or project
- 🔄 Regularly test connections

---

## Configuring LLM Settings

DataQuery AI supports multiple LLM providers. Choose the one that best fits your needs!

### Available Providers

| Provider | Best For | Pricing |
|----------|----------|---------|
| 🧠 **OpenAI** | Reliability, speed | Pay per token |
| 🌐 **OpenRouter** | Model variety | Pay per token |
| 💎 **Google Gemini** | Cost-effective | Free tier available |
| 🎭 **Anthropic Claude** | Complex reasoning | Pay per token |
| 🦙 **Ollama** | Privacy, offline use | Free (self-hosted) |

### Changing LLM Provider

1. ⚙️ Navigate to **Settings** from the navigation bar
2. 🤖 Select your preferred **LLM Provider** from the dropdown
3. 📝 Choose a **Model** (options vary by provider)
4. 🔑 Enter your **API Key**
5. 💾 Click **"Save Settings"**

### Provider-Specific Setup

#### OpenAI

**Recommended Models:**
- `gpt-4` - Most capable, best for complex queries
- `gpt-3.5-turbo` - Fast and cost-effective

**Getting an API Key:**
1. Go to [platform.openai.com](https://platform.openai.com/account/api-keys)
2. Click "Create new secret key"
3. Copy and paste into DataQuery AI settings

**Pricing:** ~$0.002-0.06 per 1K tokens

#### OpenRouter

**Benefits:**
- Access to 100+ models
- Unified API interface
- Fallback options

**Getting an API Key:**
1. Visit [openrouter.ai](https://openrouter.ai/keys)
2. Create an account
3. Generate an API key

**Popular Models:**
- `openai/gpt-4` - GPT-4 via OpenRouter
- `anthropic/claude-3-opus` - Claude 3
- `google/gemini-pro` - Gemini Pro

#### Google Gemini

**Benefits:**
- Generous free tier
- Fast responses
- Good for simple queries

**Getting an API Key:**
1. Visit [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Enable Gemini API in your Google Cloud project

#### Ollama (Local)

**Benefits:**
- Completely free
- 100% private
- No internet required

**Setup:**
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model: `ollama pull llama2`
3. Set Ollama host in settings: `http://localhost:11434`

### Testing Your Configuration

After saving settings:
1. The system will validate your API key
2. You'll see a success message if valid
3. Try a test query in the chat to confirm

### Cost Management Tips

- 📊 Monitor your usage in provider dashboards
- 🎯 Use `gpt-3.5-turbo` for simple queries
- 💰 Set up billing alerts
- 🆓 Use Gemini's free tier for testing
- 🦙 Run Ollama locally for unlimited free queries

---

## Best Practices

### Security

- 🔐 **Use strong passwords** for your DataQuery AI account
- 🔑 **Rotate API keys** regularly
- 🚫 **Never share** your credentials
- 🏢 **Use environment-specific connections** (dev/staging/prod)
- 📋 **Review query history** periodically

### Query Optimization

- 🎯 **Start broad, then narrow down** your questions
- 📅 **Specify date ranges** for time-based queries
- 🔢 **Use limits** when exploring large tables
- 📝 **Save frequently used queries** (feature coming soon)

### Data Exploration

1. **Start with Schema Questions**
   - "What tables are in this database?"
   - "What columns does the users table have?"

2. **Get a Data Overview**
   - "How many rows are in each table?"
   - "What's the date range of the orders table?"

3. **Drill Down**
   - "Show me a sample of recent orders"
   - "What are the unique values in the status column?"

### Collaboration

- 📊 **Export results** for sharing (feature coming soon)
- 💬 **Document insights** from your queries
- 🔄 **Share connection configs** with team members (safely)

---

## Troubleshooting

### Common Issues

#### 🔴 "Connection Failed" Error

**Possible Causes:**
- Incorrect connection string
- Database server not accessible
- Firewall blocking connection
- Wrong credentials

**Solutions:**
1. Double-check your connection string format
2. Verify database server is running
3. Test connection from command line:
   ```bash
   # PostgreSQL
   psql "your-connection-string"
   
   # MongoDB
   mongosh "your-connection-string"
   ```
4. Check firewall rules
5. Verify credentials are correct

---

#### 🔴 "AI Response Timeout"

**Possible Causes:**
- Complex query taking too long
- LLM provider rate limiting
- Network issues

**Solutions:**
1. Simplify your question
2. Try a different LLM provider
3. Check your internet connection
4. Wait a moment and retry

---

#### 🔴 "Invalid API Key"

**Solutions:**
1. Verify API key is copied correctly (no extra spaces)
2. Check if key has necessary permissions
3. Generate a new key if needed
4. Ensure you have billing set up (for paid providers)

---

#### 🔴 "No Results Found"

**This might mean:**
- Query genuinely returned no data
- Table/column names might be different
- Filters are too restrictive

**Try:**
1. "Show me all tables in this database"
2. "What columns does [table_name] have?"
3. Broaden your search criteria

---

### Getting Help

If you encounter persistent issues:

1. 📖 Check [TECHNICAL.md](TECHNICAL.md) for technical details
2. 🐛 Search [GitHub Issues](https://github.com/yourusername/rag-saas-platform/issues)
3. 💬 Join our [Discord community](https://discord.gg/dataqueryai)
4. 📧 Email: support@dataqueryai.com

---

## FAQ

### General Questions

**Q: Is my data secure?**
> A: Yes! Connection strings are encrypted, and the platform uses industry-standard security practices. Database credentials are never exposed in the UI.

**Q: Can I connect multiple databases?**
> A: Absolutely! You can connect as many PostgreSQL and MongoDB databases as you need.

**Q: Is there a limit on queries?**
> A: There's no limit on the platform side, but your LLM provider may have rate limits or usage quotas.

### Technical Questions

**Q: Does DataQuery AI modify my data?**
> A: No, all queries are read-only by default. The system cannot modify, delete, or insert data.

**Q: What data is stored about my database?**
> A: We store:
> - Schema information (table/column names, types)
> - Sample data (first few rows) for context
> - Your query history
> 
> We do NOT store:
> - Your full database contents
> - Sensitive data (passwords are encrypted)

**Q: Can I use this with my team?**
> A: Yes! Each team member can create their own account. Shared connections feature is coming soon.

### Billing Questions

**Q: Is DataQuery AI free?**
> A: The platform is open-source and free to use. You only pay for LLM API usage (OpenAI, etc.), which typically costs pennies per query.

**Q: How much does it cost to use?**
> A: Typical costs:
> - Simple queries: $0.001-0.01
> - Complex analysis: $0.01-0.05
> - Using Ollama: FREE!

**Q: Can I use my own LLM?**
> A: Yes! Use Ollama for local models, or any OpenAI-compatible API.

---

<div align="center">

**🎉 You're ready to start querying!**

[⬅️ Getting Started](GETTING_STARTED.md) • [⚙️ Technical Docs →](TECHNICAL.md)

</div>
