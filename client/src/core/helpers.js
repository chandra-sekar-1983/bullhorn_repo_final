class OffsetPaginator {
  constructor(fetcher, params) {
    this.fetcher = fetcher
    this.params = params
    this.limit = 16
    this.count = 0
    this.offset = 0
    this.totalCount = null
  }

  get hasNext() {
    if (this.totalCount === null) {
      return true
    }

    return this.count < this.totalCount
  }

  async next() {
    if (!this.hasNext) {
      return []
    }
    return await this.fetch()
  }

  async fetch() {
    const info = await this.fetcher(this.limit, this.offset, this.params)
    this.totalCount = info.totalCount
    this.count = info.count
    this.offset = info.offset
    return info.data
  }
}

class BatchedList {

  constructor(fetcher, params={}) {
    this.fetcher = fetcher
    this.params = params
    this.paginator = new OffsetPaginator(this.fetcher, this.params)
    this.batchSize = 5
    this.index = 0
    this.batches = {}
  }

  get len() {
    return Object.keys(this.batches).length
  }

  get batch() {
    return this.batches[this.index]
  }

  get count() {
    return this.paginator.totalCount
  }

  get info() {
    return { batch: this.batch, hasNext: this.hasNext, hasPrev: this.hasPrev }
  }

  get hasNext() {
    return this.paginator.hasNext
  }

  get hasPrev() {
    return this.index > 1
  }

  addBatch(batch) {
    this.index++
    this.batches[this.index] = batch
  }

  prev() {
    if (!this.hasPrev) {
      return []
    }

    this.index--
    return this.info
  }

  async next() {
    if (this.index < this.len) {
      this.index++
      return this.info 
    }
    this.addBatch(await this.paginator.next(this.batchSize))
    return this.info
  }
}

export {
  BatchedList,
  OffsetPaginator,
}
