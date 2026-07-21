# init email

```
Hello Professor Alwan, Professor Kadambi, and Vishwas, 
    Hope you all are doing well and thanks for your lectures and help in the past weeks!, 
    Me, Shane, and Liam have settled on a final project idea that we would like to run by you all.

    The main idea is: newer omni AI models (ex. qwen2.5-omni) take in image, audio and text as input, and are trained to refuse malicious instructions. We find that this safety really only applies for text, an instruction the model refuses when given as text is followed when packaged as an image or audio. This was confirmed locally with qwen2.5-omni-7B (https://huggingface.co/Qwen/Qwen2.5-Omni-7B). We think that this may be because of the image/audio being converted to embeddings differently from the text and skipping the safety step that text is passed through. Even hiding an effectively invisible white on white text in an image survives after screenshotting and jpeg compression.

    We would like to research the direction of combining image and audio into one injection. A change to the input image and audio that are each alone benign but form an attack when the model combines them. Like this, no single modality filter can catch the attack.

    Our rough next steps are to build the joint attack for qwen2.5-omni-3b (7b might be too expensive, and we could always generalize when we get it working), restrict that each single modality is benign alone, and then show that single modality detections miss the attack. If time allows, we would also like to build our own detector to catch this joint attack.

    We have found prior work on this: split modality injections exist for image+text (Shayegani et al 2024) and audio+text (Krishnan et al 2026); this keeps both non-text and individually benign. We found AudioHijack (Chen et al 2026) that does audio injection by convolving benign input audio with a learned malicious kernel disguised as background noise. The novelty we propose is just the combined audio+image attack, and a map of what current detectors cannot see.

    Do you all think this is reasonable for a final project? We'd especially like Prof. Alwan's and Prof. Kadambi's perspectives on the speech and imaging sides, and Vishwas' thoughts on the implementation/feasibility, or just any feedback overall.

    Thanks, 
        Boxuan, Shane, Liam

```
