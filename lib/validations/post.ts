import * as z from "zod"

export const postPatchSchema = z.object({
  title: z.string().min(3).max(128).optional(),

  // Content accepts any shape until editorjs block types are stable.
  content: z.any().optional(),
})
