<?php
require_once 'include/db_functions.php';
$db = new DB_Functions();

// json response array
$response = array("error" => FALSE);
 
if (isset($_POST['url']) && isset($_POST['platform']) && isset($_POST['user_id'])) {
 
    // receiving the post params
    $name = $_POST['name'];
    $url = $_POST['url'];
    $product_url = $_POST['product_url'];
    $track_price = $_POST['track_price'];
    $image = $_POST['image'];
    $platform = $_POST['platform'];
    $item_id = $_POST['item_id'];
    $user_id = $_POST['user_id'];
    $price = $_POST['price'];
    $variant = (isset($_POST['variant'])) ?$_POST['variant'] :NULL;
 

    $result = $db->addTrackingItem($name,$url,$product_url,$track_price,$image,$variant,$platform,$item_id,$user_id, $price);
 
    if ($result != false) {
        $response["error"] = FALSE;
        $response["msg"] = "Successful adding tracking items.";
        echo json_encode($response);
    } else {
        $response["error"] = TRUE;
        $response["error_msg"] = "Unsuccessful adding tracking items. Please try again!";
        echo json_encode($response);
    }
} else {
    // required post params is missing
    $response["error"] = TRUE;
    $response["error_msg"] = "Required parameters are missing!";
    echo json_encode($response);
}
?>