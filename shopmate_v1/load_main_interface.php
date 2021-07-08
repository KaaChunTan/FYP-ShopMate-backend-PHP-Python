<?php
$response = array();

//if(isset($_GET["keyword_search"])){

$script_to_run ='C:\xampp\htdocs\shopmate_v1\python\scrape_main_interface.py';
$result = shell_exec($script_to_run);

if(!empty($result)){
    

    $result_json = json_decode($result);  
    $response["success"] = TRUE;
    $response["result"] = $result_json;
    echo json_encode(($response),true);
}
else{

    $response["success"] = FALSE;
    $response["message"] = "Unable to scrape data from website homepage.";
    echo json_encode($response);
}
//}
?>