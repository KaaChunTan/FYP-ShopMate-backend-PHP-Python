<?php
require_once 'include/db_functions.php';
$db = new DB_Functions();

// json response array
$response = array("error" => FALSE);
 
if (isset($_POST['user_id']) && isset($_POST['item_id']) && isset($_POST['platform'])) {
 
    // receiving the post params
    $user_id = $_POST['user_id'];
    $item_id = $_POST['item_id'];
    $platform = $_POST['platform'];
 
    $result = $db->checkIfItemTracked($user_id, $item_id, $platform);
 
    if ($result != false) {
        $response["error"] = FALSE;
        $response["isTracked"] = TRUE;
        $response['tracking_id'] = $result;
        echo json_encode($response);
    } else {
        $response["error"] = FALSE;
        $response["isTracked"] = $result;
        echo json_encode($response);
    }

    // print_r($result);
} else {
    // required post params is missing
    $response["error"] = TRUE;
    $response["error_msg"] = "Required parameters are missing!";
    echo json_encode($response);
}
?>