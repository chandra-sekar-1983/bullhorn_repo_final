# Author: Jake Nielsen


class Query:
  """A Client-agnostic query interface."""
  def __init__(self, client, model_cls):
    self._client = client
    self._model_cls = model_cls
    self._filters = []
    self._order_by = []
    self._limit = None
    self._query_iterator = None

  def limit(self, limit):
    self._limit = limit
    return self

  def filter(self, field_name, cmp, value):
    self._filters.append((field_name, cmp, value))
    return self

  def order_by(self, field_name):
    self._order_by.append(field_name)
    return self

  @property
  def params(self):
    return {
      'model_cls': self._model_cls,
      'filters': self._filters,
      'order_by': self._order_by,
      'limit': self._limit,
    }

  @property
  def cursor(self):
    """Exposes the cursor of the wrapped query iterator.

    This allows the Query object to be treated like the underlying iterator if desired. e.g.:

    some_query.filter('thing', '=', 'stuff')
    async for t in some_query:
      do_something(t)
      break

    print('Current cursor is f{some_query.cursor}')
    """
    if self._query_iterator is None:
      return None

    return self._query_iterator.cursor

  def fetch(self, cursor=None):
    """Runs the query and returns the query iterator."""
    self._query_iterator = QueryIterator(self, self._client, cursor)
    return self._query_iterator

  def __aiter__(self):
    return aiter(self.fetch())


class QueryIterator:
  """QueryIterator exposes an entire set of query results as an async iterator.

  It also exposes an augmented cursor that allows each item to have a unique cursor value by
  appending an item index to the raw client cursor. This is useful for consumers that want to
  expose paginated queries with some filtering applied after the query runs, but still provide a
  consistent page size. e.g.:

  async def list_users(cursor, filter_names_containing='a'):
    q = User.all().fetch(cursor=cursor)
    page = []
    async for u in q:
      if 'a' not in u.name:
        continue

      page.append(u)
      if len(page) >= 50:
        break

    return {'users': page, 'cursor': q.cursor}
  """

  def __init__(self, query, client, cursor):
    self._query = query
    self._client = client
    self._cursor = cursor

  def __aiter__(self):
    return self._cursorized_iter()

  @property
  def cursor(self):
    return self._cursor

  async def _cursorized_iter(self):
    """Async iterator that yields results for this query iterator.

    As results are yielded, self._cursor is updated to expose an item-level cursor to the consumer.
    """

    _raw_cursor, _skip = None, 0
    if self._cursor:
      split_cursor = self._cursor.split(':')
      _raw_cursor = ':'.join(split_cursor[:-1])
      _skip = int(split_cursor[-1])

    async for item, cursor in self._itemized_iter(raw_cursor=_raw_cursor):
      if _skip > 0:
        _skip -= 1
        continue

      self._cursor = cursor
      yield item

  async def _itemized_iter(self, raw_cursor=None):
    """Async iterator that yields pairs of results with item-level cursor strings."""
    _page, _next_cursor = await self._client.run_query(cursor=raw_cursor, **self._query.params)
    while _page:
      for index, item in enumerate(_page):
        yield item, ':'.join([raw_cursor or '', str(index)])

      if not _next_cursor:
        break

      raw_cursor = _next_cursor
      _page, _next_cursor = await self._client.run_query(cursor=raw_cursor, **self._query.params)
