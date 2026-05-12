# College Policies Knowledge Base Management - Feature Guide

## Overview
The admin panel now includes a comprehensive Knowledge Base (KB) management system that allows administrators to view, search, add, and edit college policies easily.

---

## Features Added

### 1. **Search Policies**
- **Search by Keyword**: Admins can search policies using keywords
- **Language Support**: Filter results by English or Hindi
- **Real-time Results**: Shows count of matching policies

**How to Use:**
1. Go to "Knowledge Base" tab in admin panel
2. Enter a keyword in the search box (e.g., "OpenAthens", "Pearson", "registration")
3. Select the language (English/Hindi)
4. Click "Search" button
5. Results will display with policy numbers and content preview

---

### 2. **View Policies**
Each policy card displays:
- Policy number/ID
- Language indicator (English/Hindi badge)
- Full policy text in a scrollable box
- Edit and Delete buttons
- Metadata (question and answer sections)

**Card Layout:**
```
┌─────────────────────────────────────────┐
│ Policy #1              [English Badge]  │
├─────────────────────────────────────────┤
│ Question: How to access XYZ?            │
│ Answer: Follow these steps: 1... 2...   │
├─────────────────────────────────────────┤
│ [Edit Button]    [Delete Button]        │
└─────────────────────────────────────────┘
```

---

### 3. **Add New Policy**
Admins can add new policies with:
- **Question/Title**: Policy question or title
- **Answer/Details**: Comprehensive policy information
- **Language**: Select between English or Hindi

**How to Add:**
1. Scroll to "Add New Policy" section
2. Enter the question (policy title)
3. Enter the answer (detailed policy information)
4. Select language (default: English)
5. Click "Add Policy" button
6. Success notification appears
7. Newly added policy appears in search results

**Best Practices:**
- Write clear, concise questions
- Provide detailed step-by-step answers
- Use proper formatting in answers
- Keep language consistent throughout

---

### 4. **Edit Policies**
Admins can modify existing policies:

**How to Edit:**
1. Search for the policy you want to edit
2. Click the "Edit" button on the policy card
3. Edit section expands with text area
4. Modify the policy text as needed
5. Click "Save Changes" or "Cancel"
6. Changes reflect immediately

**Features:**
- Inline editing with preview
- Undo/Cancel button for accidental changes
- Visual feedback with yellow warning background
- Auto-saves after confirmation

---

### 5. **Delete Policies**
Admins can remove outdated or incorrect policies:

**How to Delete:**
1. Search for the policy you want to delete
2. Click the "Delete" button on the policy card
3. Confirmation dialog appears
4. Confirm deletion (cannot be undone)
5. Policy is permanently removed

**Warning:** Deleted policies cannot be recovered. Ensure you really want to delete before confirming.

---

## Search Query Examples

### Library & Resources
- "OpenAthens" → Find all OpenAthens-related policies
- "EBSCO" → Find EBSCO Engineering Collection policy
- "Pearson" → Find Pearson e-book policies
- "IEEE" → Find IEEE Xplore access policy
- "e-resources" → Find all e-resource access policies

### Registration & Fees
- "registration" → Find registration process policies
- "fee" → Find fee payment policies
- "semester" → Find semester-related policies
- "electives" → Find elective selection policies

### Exams & Evaluation
- "exam" → Find examination policies
- "makeup" → Find makeup exam policies
- "grades" → Find grade-related policies
- "CGPA" → Find CGPA requirement policies

### Dissertation/Project
- "dissertation" → Find dissertation policies
- "project" → Find project work policies
- "supervisor" → Find supervisor selection policies

---

## Backend Integration

### API Endpoints Used:
- **GET /admin/kb** - Fetch all KB items (with optional search query)
- **POST /admin/kb** - Add new KB item
- **PUT /admin/kb/<id>** - Update KB item
- **DELETE /admin/kb/<id>** - Delete KB item

### Data Format:
Policies are stored in `college_policy.txt` (English) and `college_policy_hi.txt` (Hindi)

**Storage Format:**
```
Question: How can I access EBSCO?
Answer: Follow these steps:
1. Visit OpenAthens
2. Search for EBSCO
3. Click on result

---

Question: Next policy question
Answer: Next policy answer
```

---

## User Interface Improvements

### Visual Enhancements:
1. **Search Section** - Green-themed input area at top
2. **Policy Cards** - Blue left border, hover shadow effect
3. **Edit Mode** - Yellow background for edit section
4. **Language Badges** - Blue badge showing policy language
5. **Results Counter** - Shows "Found X result(s)"
6. **Add Section** - Green-themed with clear fields
7. **Responsive Layout** - 3-column grid for search inputs

### Error Handling:
- "No policies found" message when search returns no results
- Error notifications if operations fail
- Confirmation dialogs for destructive actions
- Success notifications after add/edit/delete

---

## College Policies Included

The system includes 141+ college policies covering:
1. Library e-resources access (OpenAthens, EBSCO, IEEE, etc.)
2. Registration and fee payment procedures
3. Semester management and course selection
4. Examination schedules and makeup exams
5. Grade evaluation and CGPA calculations
6. Dissertation and project work requirements
7. Supervisor and mentor selection
8. Pearson e-book access procedures
9. And many more...

---

## Technical Details

### File Structure:
```
public/
├── admin.html              (Updated with KB management UI)
└── resources/
    ├── college_policy.txt   (English policies)
    └── college_policy_hi.txt (Hindi policies - if exists)

flask_app.py
├── /admin/kb (GET)         (Search & list)
├── /admin/kb (POST)        (Add new)
├── /admin/kb/<id> (PUT)    (Update)
└── /admin/kb/<id> (DELETE) (Remove)
```

### Database Format:
Policies are stored as plain text, separated by double newlines (`\n\n`)

Each policy contains:
- Question
- Answer with detailed instructions
- Step-by-step procedures
- Links and contact information

---

## Tips & Best Practices

### For Admins:
1. **Regular Updates**: Keep policies updated with latest procedures
2. **Clear Language**: Use simple, easy-to-understand language
3. **Step-by-Step**: Break complex procedures into numbered steps
4. **Contact Info**: Include support email/phone for escalations
5. **Backup**: Keep backup copies of important policies
6. **Search-Friendly**: Use common keywords in policy titles
7. **Consistent Format**: Maintain consistent Q&A format

### For Users (Students):
1. Use keywords to search for specific topics
2. Read full policy text carefully
3. Follow step-by-step instructions
4. Contact support if policy is unclear
5. Check both languages if available

---

## Troubleshooting

### Issue: Search returns no results
- **Solution**: Try different keywords or shorter terms
- Try searching just "ebsco" instead of "How can I access EBSCO"

### Issue: Cannot edit policy
- **Solution**: Make sure you have admin privileges
- Refresh page and try again

### Issue: Deleted policy by mistake
- **Solution**: Contact database admin - currently cannot recover deleted items
- **Prevention**: Always confirm before deleting

### Issue: Policy text not displaying correctly
- **Solution**: Check browser console for errors
- Clear cache and refresh page

---

## Future Enhancements

Possible features to add:
1. **Version History** - Track changes to policies
2. **Bulk Operations** - Edit multiple policies at once
3. **Export/Import** - Backup and restore policies
4. **Access Control** - Different permission levels for admins
5. **Policy Categories** - Organize by topic/department
6. **Translation Help** - AI-assisted Hindi translations
7. **Feedback Rating** - Students rate policy helpfulness
8. **Analytics** - Track most-searched policies

---

## Support

For issues or questions:
- Contact the WILP Library: narendra.bhoi@pilani.bits-pilani.ac.in
- Email Support: support@wilp.bits-pilani.ac.in
- Technical Issues: Submit bug report with screenshot
