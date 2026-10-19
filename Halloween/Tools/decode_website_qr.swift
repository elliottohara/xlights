import Foundation
import CoreImage
let context = CIContext(options: nil)
let detector = CIDetector(ofType: CIDetectorTypeQRCode, context: context, options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])!
for path in CommandLine.arguments.dropFirst() {
    let image = CIImage(contentsOf: URL(fileURLWithPath: path))!
    let features = detector.features(in: image).compactMap { ($0 as? CIQRCodeFeature)?.messageString }
    print(path + " " + features.joined(separator: " | "))
    guard features == ["https://oharafamilylightshow.com/"] else { exit(1) }
}
