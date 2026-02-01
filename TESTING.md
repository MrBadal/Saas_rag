# Testing Guide

## Testing Strategy

### Test Pyramid
- **Unit Tests**: Individual functions and classes
- **Integration Tests**: API endpoints and database operations
- **System Tests**: End-to-end user workflows
- **Load Tests**: Performance under load

## Backend Testing

### Setup Test Environment

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_connectors.py

# Verbose output
pytest -v
```

### Unit Tests

**Test Database Connectors:**
```python
# tests/test_connectors.py
import pytest
from app.services.connectors import PostgreSQLConnector, MongoDBConnector

def test_postgresql_connection():
    connector = PostgreSQLConnector()
    # Test with valid connection string
    assert connector.connect("postgresql://user:pass@localhost:5432/testdb")
    
def test_schema_extraction():
    connector = PostgreSQLConnector()
    connector.connect("postgresql://...")
    schema = connector.get_schema()
    assert isinstance(schema, dict)
    assert len(schema) > 0
```

**Test RAG Service:**
```python
# tests/test_rag_service.py
import pytest
from app.services.rag_service import RAGService

def test_embedding_generation():
    rag = RAGService()
    schema = {"users": [{"name": "id", "type": "int"}]}
    vector_store = rag.create_vector_store(1, schema, [])
    assert vector_store is not None

def test_query_generation():
    rag = RAGService()
    schema = {"users": [{"name": "id", "type": "int"}]}
    query = rag.generate_query("find all users", schema, "postgresql")
    assert "SELECT" in query.upper()
```

### Integration Tests

**Test API Endpoints:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_connection():
    # Login first
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Create connection
    response = client.post(
        "/api/connections/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test DB",
            "db_type": "postgresql",
            "connection_string": "postgresql://..."
        }
    )
    assert response.status_code == 200
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

### Run Tests

```bash
# All tests
npm test

# Coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Component Tests

```javascript
// src/components/__tests__/Login.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import Login from '../Login';

test('renders login form', () => {
  render(<Login onLogin={() => {}} />);
  expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
});

test('submits login form', async () => {
  const mockLogin = jest.fn();
  render(<Login onLogin={mockLogin} />);
  
  fireEvent.change(screen.getByLabelText(/Email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/Password/i), {
    target: { value: 'password123' }
  });
  fireEvent.click(screen.getByText(/Login/i));
  
  // Assert API call was made
});
```

## End-to-End Testing

### Manual Test Cases

#### Test Case 1: User Registration & Login
1. Navigate to `/login`
2. Click "Register"
3. Enter email and password
4. Verify redirect to dashboard
5. Logout and login again
6. Verify successful authentication

**Expected Result:** User can register, login, and access dashboard

#### Test Case 2: Database Connection
1. Login to application
2. Navigate to "Connections"
3. Click "Add Connection"
4. Enter PostgreSQL connection details:
   - Name: "Test Database"
   - Type: PostgreSQL
   - Connection String: `postgresql://user:pass@host:5432/db`
5. Click "Create Connection"
6. Verify connection appears in list
7. Verify schema is displayed

**Expected Result:** Connection is created and schema is indexed

#### Test Case 3: Natural Language Query
1. Navigate to "Chat"
2. Select a database connection
3. Enter query: "What tables are in my database?"
4. Submit query
5. Verify AI response
6. Try query: "Show me all users"
7. Verify generated SQL query
8. Verify results are displayed

**Expected Result:** AI provides relevant answers with optional query generation

#### Test Case 4: Query History
1. Execute multiple queries
2. Navigate to query history
3. Verify all queries are logged
4. Verify timestamps are correct

**Expected Result:** Query history is maintained

### Automated E2E Testing (Playwright)

```bash
npm install --save-dev @playwright/test
```

```javascript
// e2e/user-flow.spec.js
const { test, expect } = require('@playwright/test');

test('complete user flow', async ({ page }) => {
  // Register
  await page.goto('http://localhost:3000/login');
  await page.click('text=Register');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Register")');
  
  // Verify dashboard
  await expect(page).toHaveURL(/.*dashboard/);
  
  // Add connection
  await page.click('text=Connections');
  await page.click('text=Add Connection');
  await page.fill('input[placeholder="My Database"]', 'Test DB');
  await page.fill('input[placeholder*="postgresql"]', 'postgresql://...');
  await page.click('button:has-text("Create Connection")');
  
  // Query database
  await page.click('text=Chat');
  await page.fill('input[placeholder*="Ask"]', 'What tables exist?');
  await page.click('button:has-text("Send")');
  
  // Verify response
  await expect(page.locator('.message')).toContainText('table');
});
```

## Load Testing

### Using Locust

```bash
pip install locust
```

```python
# locustfile.py
from locust import HttpUser, task, between

class RAGPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def query_database(self):
        self.client.post(
            "/api/query/",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "connection_id": 1,
                "query": "What tables are in my database?"
            }
        )
    
    @task(1)
    def list_connections(self):
        self.client.get(
            "/api/connections/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## Performance Benchmarks

### Target Metrics
- API response time: < 200ms (p95)
- Vector search: < 100ms
- LLM response: < 3s
- Database query: < 500ms
- Concurrent users: 100+

### Monitoring During Tests
- CPU usage
- Memory consumption
- Database connections
- API error rates
- LLM API costs

## Test Data

### Sample PostgreSQL Database

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (email, name) VALUES
    ('john@example.com', 'John Doe'),
    ('jane@example.com', 'Jane Smith');

INSERT INTO orders (user_id, amount, status) VALUES
    (1, 99.99, 'completed'),
    (1, 149.99, 'pending'),
    (2, 79.99, 'completed');
```

### Sample MongoDB Database

```javascript
db.customers.insertMany([
  {
    name: "Alice Johnson",
    email: "alice@example.com",
    orders: [
      { product: "Laptop", price: 999 },
      { product: "Mouse", price: 29 }
    ]
  },
  {
    name: "Bob Williams",
    email: "bob@example.com",
    orders: [
      { product: "Keyboard", price: 79 }
    ]
  }
]);
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
```

## Troubleshooting Tests

### Common Issues

**Database connection fails:**
- Ensure test database is running
- Check connection string format
- Verify network access

**Vector store errors:**
- Install pgvector extension
- Check PostgreSQL version (15+)
- Verify embedding dimensions

**LLM API failures:**
- Check API key validity
- Monitor rate limits
- Use mock responses for unit tests

**Frontend test timeouts:**
- Increase timeout values
- Mock API responses
- Check async handling
