CREATE TABLE movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    app_id VARCHAR(50),
    url VARCHAR(500),
    FOREIGN KEY (app_id) REFERENCES games(app_id)
);
