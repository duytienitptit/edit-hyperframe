// Detect faces (and upper bodies as fallback) with Apple Vision.
// Usage: swift tools/faces.swift <img1> [img2 ...]  > faces.json
// Output: {"<path>": {"w":W,"h":H,"faces":[[x,y,w,h],...],"bodies":[[x,y,w,h],...]}} — normalized, origin TOP-left.
import Foundation
import Vision
import AppKit

var out: [String: Any] = [:]
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    let fr = VNDetectFaceRectanglesRequest()
    let hr = VNDetectHumanRectanglesRequest()
    hr.upperBodyOnly = true
    try? handler.perform([fr, hr])
    func boxes(_ obs: [VNDetectedObjectObservation]?) -> [[Double]] {
        (obs ?? []).map { o in
            let b = o.boundingBox
            return [Double(b.minX), Double(1 - b.maxY), Double(b.width), Double(b.height)]
        }
    }
    out[path] = ["w": cg.width, "h": cg.height,
                 "faces": boxes(fr.results), "bodies": boxes(hr.results)]
}
let data = try! JSONSerialization.data(withJSONObject: out, options: [.prettyPrinted, .sortedKeys])
print(String(data: data, encoding: .utf8)!)
