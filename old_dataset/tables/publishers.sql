CREATE TABLE publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    app_id VARCHAR(50),
    name VARCHAR(255),
    FOREIGN KEY (app_id) REFERENCES games(app_id)
);
