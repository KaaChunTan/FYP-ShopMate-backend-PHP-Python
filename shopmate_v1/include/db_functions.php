<?php
 
/**
 * @author Ravi Tamada
 * @link https://www.androidhive.info/2012/01/android-login-and-registration-with-php-mysql-and-sqlite/ Complete tutorial
 */
 
class DB_Functions {
 
    private $conn;
 
    // constructor
    function __construct() {
        require_once 'db_connect.php';
        // connecting to database
        $db = new Db_Connect();
        $this->conn = $db->connect();
    }
 
    // destructor
    function __destruct() {
         
    }
 
    /**
     * Storing new user
     * returns user details
     */
    public function storeUser($name, $email, $password,$token) {
        $uuid = uniqid('', true);
        $hash = $this->hashSSHA($password);
        $encrypted_password = $hash["encrypted"]; // encrypted password
        $salt = $hash["salt"]; // salt
 
        $stmt = $this->conn->prepare("INSERT INTO users(unique_id, name, email, encrypted_password, salt, created_at,token) VALUES(?, ?, ?, ?, ?, NOW(),?)");
        $stmt->bind_param("ssssss", $uuid, $name, $email, $encrypted_password, $salt,$token);
        $result = $stmt->execute();
        $stmt->close();
 
        // check for successful store
        if ($result) {
            $stmt = $this->conn->prepare("SELECT * FROM users WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $user = $stmt->get_result()->fetch_assoc();
            $stmt->close();
 
            return $user;
        } else {
            return false;
        }
    }
 
    /**
     * Get user by email and password
     */
    //update the code because older version of php will ignore the code when the object is null
    //which means although user returned is false, the code below just ignored.
    //but newer php version cannot do this, so it cause error, so need to set if else condition
    public function getUserByEmailAndPassword($email, $password) {
 
        $stmt = $this->conn->prepare("SELECT * FROM users WHERE email = ?");
 
        $stmt->bind_param("s", $email);
 
        if ($stmt->execute()) {
            $user = $stmt->get_result()->fetch_assoc();
            $stmt->close();
 
            // verifying user password
            if($user!=false){

                $salt = $user['salt'];
                $encrypted_password = $user['encrypted_password'];
                $hash = $this->checkhashSSHA($salt, $password);
                // check for password equality
                if ($encrypted_password == $hash) {
                    // user authentication details are correct
                    return $user;
                }
                else{
                    return false; //false if the password is incorrect
                }
            }
            else{
                return false; //false if the get_result() returns false
            }
            
            
        } else {
            return false; //false if the statement cannot be executed
        }
    }
 
    /**
     * Check user is existed or not
     */
    public function isUserExisted($email) {
        $stmt = $this->conn->prepare("SELECT email from users WHERE email = ?");
 
        $stmt->bind_param("s", $email);
 
        $stmt->execute();
 
        $stmt->store_result();
 
        if ($stmt->num_rows > 0) {
            // user existed 
            $stmt->close();
            return true;
        } else {
            // user not existed
            $stmt->close();
            return false;
        }
    }
 
    /**
     * Encrypting password
     * @param password
     * returns salt and encrypted password
     */
    public function hashSSHA($password) {
 
        $salt = sha1(rand());
        $salt = substr($salt, 0, 10);
        $encrypted = base64_encode(sha1($password . $salt, true) . $salt);
        $hash = array("salt" => $salt, "encrypted" => $encrypted);
        return $hash;
    }
 
    /**
     * Decrypting password
     * @param salt, password
     * returns hash string
     */
    public function checkhashSSHA($salt, $password) {
 
        $hash = base64_encode(sha1($password . $salt, true) . $salt);
 
        return $hash;
    }

    public function updateFCMtoken($user_id, $token) {
 
        $stmt = $this->conn->prepare("UPDATE users SET token = ? WHERE unique_id = ?;");
        $stmt->bind_param("ss", $token, $user_id);
        $result = $stmt->execute();
        $stmt->close();

        return TRUE;
    }

    /**
     * Add new item into the tracking list
     */
    public function addTrackingItem($name,$url,$product_url,$track_price,$image,$variant,$platform,$item_id,$user_id, $price){
        $uuid = uniqid('', true);

        if(!is_null($variant)){
            $stmt = $this->conn->prepare("INSERT INTO track_items(unique_id, name, url, product_url, track_price, image, variant, platform, item_id, user_id) VALUES(?,?,?,?,?,?,?,?,?,?)");
            $stmt->bind_param("ssssssssss",$uuid, $name,$url,$product_url,$track_price,$image,$variant,$platform,$item_id,$user_id);
            $result = $stmt->execute();
            $stmt->close();
        }
        else{
            $stmt = $this->conn->prepare("INSERT INTO track_items(unique_id, name, url, product_url, track_price, image, platform, item_id, user_id) VALUES(?,?,?,?,?,?,?,?,?)");
            $stmt->bind_param("sssssssss", $uuid, $name,$url,$product_url,$track_price,$image,$platform,$item_id,$user_id);
            $result = $stmt->execute();
            $stmt->close();
        }

        $stmt = $this->conn->prepare("INSERT INTO price_tracking(price,tracked_item_id) VALUES(?,?)");
        $stmt->bind_param("ss",$price, $uuid);
        $result = $stmt->execute();
        $stmt->close();

        if($result){
            return true;
        }
        else{
            return false;
        }

    }
 
    public function removeTrackingItem($uuid,$user_id){

        $stmt = $this->conn->prepare("DELETE FROM track_items WHERE unique_id = ? AND user_id = ?");
        $stmt->bind_param("ss", $uuid, $user_id);
        $result = $stmt->execute();
        $stmt->close();

        if($result){
            return true;
        }
        else{
            return false;
        }

    }

    public function getTrackingItem($user_id){

        $stmt = $this->conn->prepare("SELECT * FROM ((SELECT * FROM track_items WHERE user_id = ?) AS t JOIN ( SELECT * FROM price_tracking WHERE tracking_id IN ( SELECT MAX(tracking_id) FROM price_tracking GROUP BY tracked_item_id ) ) AS latest_price_tracking ON t.unique_id = latest_price_tracking.tracked_item_id)");
        $stmt->bind_param("s", $user_id);
        $items["tracked_items"] = array();

        if ($stmt->execute()){
            $result = $stmt->get_result();
            while($row = $result->fetch_assoc()) {
                //temp item array
                $tracked_items = array();
                $tracked_items["unique_id"] = $row["unique_id"];
                $tracked_items["name"] = $row["name"];
                $tracked_items["url"] = $row["url"];
                $tracked_items["product_url"] = $row["product_url"];
                $tracked_items["track_price"] = $row["track_price"];
                $tracked_items["latest_price"] = $row["price"];
                $tracked_items["image"] = $row["image"];
                $tracked_items["variant"] = $row["variant"];
                $tracked_items["platform"] = $row["platform"];
         
                // push single product into final response array
                array_push($items["tracked_items"], $tracked_items);
            }
            $stmt->close();
            return $items;
        } else {
            return false;
        } 

    }

    public function getPriceHistory($uuid){

        $stmt = $this->conn->prepare("SELECT * FROM price_tracking WHERE tracked_item_id = ?");
        $stmt->bind_param("s", $uuid);
        $items["price_tracking"] = array();

        if ($stmt->execute()){
            $result = $stmt->get_result();
            while($row = $result->fetch_assoc()) {
                //temp item array
                $temp = array();
                $temp["track_date"] = $row["track_date"];
                $temp["price"] = $row["price"];
         
                // push single product into final response array
                array_push($items["price_tracking"], $temp);
            }
            $stmt->close();
            return $items;
        } else {
            return false;
        } 

    }

    public function addPriceTracking($price, $uuid){
        $stmt = $this->conn->prepare("INSERT INTO price_tracking(price,tracked_item_id) VALUES(?,?)");
        $stmt->bind_param("ss", $price, $uuid);
        $result = $stmt->execute();
        $stmt->close();
    }

    //get the last tracked price of the item so that can compare with the latest tracked price
    public function getLastTrackedPrice($uuid){

        $stmt  = $this->conn->prepare("SELECT price FROM price_tracking WHERE tracked_item_id = ? ORDER BY tracking_id DESC LIMIT 1");
        $stmt->bind_param("s",$uuid);
        $stmt->execute();
        $stmt->store_result();    
        $stmt->bind_result($last_price);  // number of arguments must match columns in SELECT
        if($stmt->num_rows > 0) {
            while ($stmt->fetch()) {
                return $last_price;  
            }
        }
        $stmt->close();
        
    }

    // return array of the tracked item info so that to track it later
    public function getTrackingItemUrl(){
        $stmt = $this->conn->prepare("SELECT unique_id, url, variant, platform FROM track_items");
    
        if ($stmt->execute()){
            $result = $stmt->get_result()->fetch_all();
            return $result;
        }
    }

    public function test(){
        $stmt = $this->conn->prepare("INSERT INTO test(id) VALUES (200)");
        $stmt->execute();
        $stmt->close();
    }

    public function checkIfItemTracked($user_id, $item_id, $platform){
        $stmt  = $this->conn->prepare("SELECT unique_id FROM track_items WHERE user_id = ? and item_id = ? and platform = ?");
        $stmt->bind_param("sss", $user_id, $item_id, $platform);
        $stmt->execute();
        $stmt->store_result();    
        $stmt->bind_result($tracking_id);  // number of arguments must match columns in SELECT
        if($stmt->num_rows > 0) {
            while ($stmt->fetch()) {
                return $tracking_id;  
            }
        }
        else{
            return false;
        }
        $stmt->close();
    }

    public function getUserNotifications($uuid){

        $stmt = $this->conn->prepare("SELECT * FROM notifications WHERE user_id = ? ORDER BY notification_id DESC");
        $stmt->bind_param("s", $uuid);
        $items["notifications"] = array();

        if ($stmt->execute()){
            $result = $stmt->get_result();
            while($row = $result->fetch_assoc()) {
                //temp item array
                $temp = array();
                $temp["notification_id"] = $row["notification_id"];
                $temp["image_url"] = $row["image_url"];
                $temp["message"] = $row["message"];
                $temp["datetime"] = $row["datetime"];
                $temp["isRead"] = $row["isRead"];
                $temp["item_name"] = $row["item_name"];
         
                // push single product into final response array
                array_push($items["notifications"], $temp);
            }
            $stmt->close();
            return $items;
        } else {
            return false;
        } 

    }

    public function markNotificationAsRead($notification_id){

        $stmt = $this->conn->prepare("UPDATE notifications SET isRead = 1 WHERE notifications.notification_id = ?");
        $stmt->bind_param("s",$notification_id);
        $result = $stmt->execute();
        $stmt->close();

        if($result){
            return true;
        }
        else{
            return false;
        }

    }

    public function getUserNotificationsCount($uuid){
        $stmt = $this->conn->prepare("SELECT COUNT(*) FROM notifications WHERE notifications.user_id = ? AND notifications.isRead = 0");
        $stmt->bind_param("s",$uuid);
        $stmt->execute();
        $stmt->store_result();    
        $stmt->bind_result($notification_count); 
        if($stmt->num_rows > 0) {
            while ($stmt->fetch()) {
                return $notification_count;  
            }
        }
        else{
            return false;
        }
        $stmt->close();


    }
}
 
?>