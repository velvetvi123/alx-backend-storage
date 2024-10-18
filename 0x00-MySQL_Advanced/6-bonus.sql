-- Creates a stored procedure AddBonus to add corrections
DELIMITER $$
CREATE PROCEDURE AddBonus(
    IN user_id INT,
    IN project_name VARCHAR(255),
    IN score INT
)
BEGIN
    DECLARE project_id INT;
    
    -- Try to get the project id if it exists
    SELECT id INTO project_id 
    FROM projects 
    WHERE name = project_name;
    
    -- If project doesn't exist, create it
    IF project_id IS NULL THEN
        INSERT INTO projects (name) VALUES (project_name);
        SET project_id = LAST_INSERT_ID();
    END IF;
    
    -- Insert the correction
    INSERT INTO corrections (user_id, project_id, score)
    VALUES (user_id, project_id, score);
END$$
DELIMITER ;
