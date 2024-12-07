CREATE TABLE subpackages (
    subpackage_id INT AUTO_INCREMENT PRIMARY KEY,
    package_id INT,
    title VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    FOREIGN KEY (package_id) REFERENCES packages(package_id)
);
