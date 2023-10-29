
CREATE TABLE request(
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                country VARCHAR(255),
                gender ENUM('Male', 'Female'),
                age ENUM('0-16', '17-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+'),
                income ENUM('0-10k', '10k-20k', '20k-40k', '40k-60k', '60k-100k', '100k-150k', '150k-250k', '250k+'),
                is_banned BOOLEAN,
                client_ip VARCHAR(255),
                time_of_request TIMESTAMP);


CREATE TABLE request_time(
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                request_time TIMESTAMP,
                requested_file VARCHAR(255),
                error_code INT
                    )
