## Using Initial Job Listing provided by GreedyModel
1. Create a `GreedyModel` instance
2. Call `GreedyModel.generate_initial_job_listing()`
  The function has a parameter `shared_job_order`, which is a list of job ids. If this parameter is not provided, the function will use WEDD list to generate a shared job order instead.

3. After the function is called, it will return a list of list, which is the initial job listing and can be used to put into `job_orders_on_machines` parameter of `generate_schedule()` written by HsiaoLi-Yeh.