<?php
 //get info from the trackitems table //
 //run the python script //
 //retrieve the last tracked price //
 //save the return price to the table   //
 //compare price (make sure it is not None), if there is a price drop, send a fcm to the user with the registration token
 
 $db = mysqli_connect("localhost","root","","shopmate");
 if($db === false){
     die("ERROR: Could not connect. ". mysqli_connect_error());
 }

// $tracked_item_info = $db->getTrackingItemUrl();
$stmt = $db->prepare("SELECT unique_id, url, variant, platform FROM track_items");
    
if ($stmt->execute()){
    $tracked_item_info = $stmt->get_result()->fetch_all();
    
}

foreach($tracked_item_info as $row){
    $uuid = $row['0'];
    $url = $row['1'];
    $variant = $row['2'];
    $platform = $row['3'];


    $last_tracked_price = $db->getLastTrackedPrice($uuid);
    echo "last tracked price: " .$last_tracked_price. "\n";

    //if variant is null, then no need send to the terminal to run
    if(!is_null($variant)){
        $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\scrape_price_tracking.py';
        $price = shell_exec($script_to_run." "."\"". $url."\""." ". $platform." "."\"". $variant. "\"");

    }
    else{
        $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\scrape_price_tracking.py';
        $price = shell_exec($script_to_run." "."\"". $url."\""." ". $platform);

    }

    echo "new price: " .$price. "\n";
    $db->addPriceTracking($price,$uuid);

    sleep(3);
}














 

?>