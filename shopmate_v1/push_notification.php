<?php 

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
    //    curl_setopt ($ch, CURLOPT_SSL_VERIFYHOST, 0);  
    //    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
       curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($fields));
       $result = curl_exec($ch);           
       if ($result === FALSE) {
           die('Curl failed: ' . curl_error($ch));
       }
       curl_close($ch);
       return $result;
	}
	
    $uuid = "607ee63eddfea1.87585942";
    $token = "";

    $link = mysqli_connect("localhost","root","","shopmate");
    if($link === false){
        die("ERROR: Could not connect. ". mysqli_connect_error());
    }
    $last_tracked_price = "200.00" ;
    $price = "121.90";
   
    //compare last tracked price with the new scraped price
    if($last_tracked_price != "None" && $price !="None"){
        $old_price = floatval($last_tracked_price);
        $new_price = floatval($price);

        if($new_price < $old_price){
            $stmt  = $link->prepare("SELECT token FROM users WHERE unique_id = ? ");
            $stmt->bind_param("s",$uuid);
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
        }
    }



 ?>
