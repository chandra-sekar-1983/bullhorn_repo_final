# Logging

| ENV VAR | DEFAULT |
| --- | --- |
| LOGGING_NAME | 'dpi' |
| LOGGING_LEVEL | 'TRACE' |
| LOGGING_FORMATTER | 'JSONFormatter' |
| LOGGING_GCP_PROJECT_ID | None |

# Formatter options
| TextFormatter
| JSONFormatter
| GCPFormatter

Update the formatter through environment variable *LOGGING_FORMATTER* or inject into the LoggerClient

# Usage
```python
from core.logging import logger


logger.trace('message')
logger.debug('message')
logger.warning('message')
logger.info('message')
logger.error('message')
logger.critical('message')
```
