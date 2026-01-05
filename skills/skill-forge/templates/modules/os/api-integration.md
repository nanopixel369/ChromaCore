<L1>
## API Integration Workflow

### Step 1: Validate Input

Check required parameters:
- API endpoint URL
- Authentication credentials
- Request payload/parameters

### Step 2: Prepare Request

Configure HTTP request:
- Method (GET/POST/PUT/DELETE)
- Headers (auth, content-type, etc)
- Body/parameters
- Timeout settings

### Step 3: Execute Request

Send HTTP request with error handling:
- Network errors
- Timeout errors
- HTTP error codes

### Step 4: Validate Response

Check response:
- Status code (2xx = success)
- Response format (JSON/XML/text)
- Schema validation
- Data completeness

### Step 5: Process Result

Transform response:
- Extract relevant data
- Format for output
- Handle pagination if needed
</L1>

## Request Configuration

retry_count: $retry-default  <!-- L2: tunable -->
timeout_seconds: $timeout-default  <!-- L2: tunable -->
