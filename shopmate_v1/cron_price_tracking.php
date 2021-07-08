<?php
 //get info from the trackitems table //
 //run the python script //
 //retrieve the last tracked price //
 //save the return price to the table   //
 //compare price (make sure it is not None), if there is a price drop, send a fcm to the user with the registration token

 
    function send_notification ($token, $message)
    {
        
        $url = 'https://fcm.googleapis.com/fcm/send';
        $fields = array(
            'to' => $token,
            'notification' => $message,
            'priority' => "high"
            );

        $headers = array(
            'Authorization:key = AAAABREnD00:APA91bGLeth4xRzA4dp7SwodhiJCfBvmx_3wGm9LZQYXFCUGkosv1Z8Tkrrqd8seDKVEF85gqbc2to30CmzEluhe3_6lmMEm_tZp0AIolazyX3lZqEqKDd9dcwsMtzrnHVuVM50fc43y ',
            'Content-Type: application/json'
            );

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($fields));
        $result = curl_exec($ch);           
        if ($result === FALSE) {
            die('Curl failed: ' . curl_error($ch));
        }
        curl_close($ch);
        return $result;
    }

    $db = mysqli_connect("localhost","root","","shopmate");
    if($db === false){
        die("ERROR: Could not connect. ". mysqli_connect_error());
    }

    // $tracked_item_info = $db->getTrackingItemUrl();
    $stmt = $db->prepare("SELECT unique_id, url, variant, platform, user_id,image,name FROM track_items");
        
    if ($stmt->execute()){
        $tracked_item_info = $stmt->get_result()->fetch_all();    
    }
    $stmt->close();

    foreach($tracked_item_info as $row){
        $uuid = $row['0'];
        $url = $row['1'];
        $variant = $row['2'];
        $platform = $row['3'];
        $user_id = $row['4'];
        $image = $row['5'];
        $name = $row['6'];


        #$last_tracked_price = $db->getLastTrackedPrice($uuid);
        $last_tracked_price = "";
        $stmt  = $db->prepare("SELECT price FROM price_tracking WHERE tracked_item_id = ? ORDER BY tracking_id DESC LIMIT 1");
        $stmt->bind_param("s",$uuid);
        $stmt->execute();
        $stmt->store_result();    
        $stmt->bind_result($last_price);  // number of arguments must match columns in SELECT
        if($stmt->num_rows > 0) {
            while ($stmt->fetch()) {
                $last_tracked_price = $last_price;  
            }
        }
        $stmt->close();


        //echo "last tracked price: " .$last_tracked_price. "\n";
        $price = "";
        //if variant is null, then no need send to the terminal to run
        if(!is_null($variant)){
            $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\scrape_price_tracking.py';
            $price = shell_exec($script_to_run." "."\"". $url."\""." ". $platform." "."\"". $variant. "\"");

        }
        else{
            $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\scrape_price_tracking.py';
            $price = shell_exec($script_to_run." "."\"". $url."\""." ". $platform);

        }

        //echo "new price: " .$price. "\n";

        // insert the new price into the database
        $stmt = $db->prepare("INSERT INTO price_tracking(price,tracked_item_id) VALUES(?,?)");
        $stmt->bind_param("ss", $price, $uuid);
        $result = $stmt->execute();
        $stmt->close();
        sleep(3);

        //compare last tracked price with the new scraped price
        if($last_tracked_price != "None" && $price !="None"){
            $old_price = floatval($last_tracked_price);
            $new_price = floatval($price);

            if($new_price < $old_price){
                $stmt  = $db->prepare("SELECT token FROM users WHERE unique_id = ? ");
                $stmt->bind_param("s",$user_id);
                $stmt->execute();
                $stmt->store_result();    
                $stmt->bind_result($tok);  // number of arguments must match columns in SELECT
                if($stmt->num_rows > 0) {
                    while ($stmt->fetch()) {
                        $token = $tok;  
                    }
                }
                $stmt->close();


                $message = array(
                    "title" => "Price drop alert!",
                    "body" => "Let's check it out");
                $message_status = send_notification($token, $message);
                echo $message_status;

                //insert data into the notification table
                $message_title = "Price drop alert!";
                $stmt = $db->prepare("INSERT INTO notifications(image_url,message,item_name,user_id) VALUES(?,?,?,?)");
                $stmt->bind_param("ssss", $image,$message_title,$name,$user_id);
                $result = $stmt->execute();
                $stmt->close();
            }
        }
    }














 

?>