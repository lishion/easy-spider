# thin spider
## 基本结构
* resource: 资源
* handler: 具体的处理手段    
* filter: 对资源进行筛选
* resource_queue: 对资源进行分发
* request: 对资源进行获取
* response: 响应包装
* extractor: 提取response中的链接
* filter: 过滤器
* spider: 爬虫具体逻辑
* core: 运行爬虫
* wrapper: 包装器