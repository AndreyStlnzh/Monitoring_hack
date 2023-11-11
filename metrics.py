from ensemble_boxes import weighted_boxes_fusion


def compute_metrics(boxes, confidences, weights, iou_thr=0.5, skip_box_thr=0.001):
    """
    Computes WBF metrics for bounding boxes and confidences
    """
    labels = [[0 for _ in conf] for conf in confidences]
    res = weighted_boxes_fusion(boxes, confidences, labels,
                                weights=weights, iou_thr=iou_thr, skip_box_thr=skip_box_thr)
    return [res[0].tolist(), res[1].tolist()]
