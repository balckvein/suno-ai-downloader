// Login to https://suno.com/me
copy(
  [
    "song_name,song_url,song_prompt",
    ...[
      ...$('[role="grid"]')[
        Object.keys($('[role="grid"]')).filter((x) =>
          x.startsWith("__reactProps")
        )[0]
      ].children[0].props.values[0][1].collection,
    ]
      .filter((x) => x.value.audio_url)
      .map((x) => {
        const title = x.value.title.trim() || x.value.id;
        // Use a hash of the song's ID for consistency
        const hash = x.value.id.slice(0, 5); // Use the first 5 characters of the ID
        // Get UUID from the song's ID
        const uuid = x.value.id;
        // Format filename: lowercase, replace spaces with dashes, add id and hash
        const formattedTitle = `${title
          .toLowerCase()
          .replace(/\s+/g, "-")}-id-${hash}`;

        // Find the description from the DOM using the song ID
        const songElement = document.querySelector(
          `[data-clip-id="${x.value.id}"]`
        );
        let description = "";
        if (songElement) {
          const descriptionSpan = Array.from(
            songElement.querySelectorAll("span[title]")
          ).find((span) => span.textContent.trim().length > 50);
          description = descriptionSpan
            ? descriptionSpan.getAttribute("title").trim()
            : "No description available";
        }

        // Include original UUID filename in the description
        const fullDescription = `Original filename: ${uuid}.mp3\n\nPrompt:\n${description}`;

        // Escape double quotes for CSV and remove any trailing newline
        const escapedDescription = fullDescription
          .replace(/"/g, '""')
          .replace(/\n$/, "");

        // Always wrap description in quotes for consistency
        return `${formattedTitle}.mp3,${
          x.value.audio_url
        },"${escapedDescription}"`;
      }),
  ]
    .join("\n")
    .trim() // Trim any extra whitespace/newlines from the final output
);
