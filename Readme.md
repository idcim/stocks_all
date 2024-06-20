# stocks_all
- Docker image
    image: idcims/stocks_all
- Docker yml
    docker-compose.yml
- ENV
  ```
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=root
    DB_NAME=gu
    DB_PREFIX=api_
    TASKS_TABLE=tasks
    TASKS_TABLE_RESPONSE=task_responses
  ```
- Database Table
  - api_tasks
    ```SQL
      CREATE TABLE `api_tasks` (
        `id` int(11) NOT NULL,
        `target_url` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
        `method` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
        `post_body` text COLLATE utf8_unicode_ci,
        `header` text COLLATE utf8_unicode_ci,
        `frequency` int(11) NOT NULL COMMENT '每秒发送请求数',
        `times` int(11) NOT NULL,
        `data_array` text COLLATE utf8_unicode_ci NOT NULL,
        `callback_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
        `status` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
        `times_completed` int(11) DEFAULT '0',
        `last_result` text COLLATE utf8_unicode_ci,
        `error_message` text COLLATE utf8_unicode_ci,
        `completed_at` datetime DEFAULT NULL
      ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
    ```
  
  - api_task_responses
    ```SQL
      CREATE TABLE `api_task_responses` (
        `id` int(11) NOT NULL,
        `task_id` int(11) NOT NULL,
        `response_data` text COLLATE utf8_unicode_ci NOT NULL,
        `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
      ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
    ```