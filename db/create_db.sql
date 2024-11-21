DROP TABLE IF EXISTS restaurant_hours;
DROP TABLE IF EXISTS restaurants;

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,               
    name VARCHAR(255) NOT NULL,         
    hours TEXT                            
);

CREATE TABLE restaurant_hours (
    id SERIAL PRIMARY KEY,               
    restaurant_id INT NOT NULL,          
    day VARCHAR(10) NOT NULL,           
    opening_time TIME NOT NULL,          
    closing_time TIME NOT NULL,          
    CONSTRAINT fk_restaurant
        FOREIGN KEY (restaurant_id)      
        REFERENCES restaurants (id)
        ON DELETE CASCADE                
);

CREATE INDEX idx_restaurant_name ON restaurants(name);                    
CREATE INDEX idx_restaurant_hours_day ON restaurant_hours(restaurant_id, day); 
CREATE INDEX idx_opening_time ON restaurant_hours(opening_time);        
CREATE INDEX idx_closing_time ON restaurant_hours(closing_time);        
