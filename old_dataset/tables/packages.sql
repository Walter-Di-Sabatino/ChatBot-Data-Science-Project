CREATE TABLE packages (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    app_id VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    FOREIGN KEY (app_id) REFERENCES games(app_id)
);
