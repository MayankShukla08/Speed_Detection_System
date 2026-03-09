# Combined Violations Dataset

This dataset merges the previously separate `violation_record` and `violations` collections into a unified structure that tracks the complete lifecycle of traffic violations.

## Structure Overview

The combined dataset includes fields from both original collections:

### Key Fields
- **License Plate**: Vehicle license plate number
- **Violation Date**: When the violation occurred
- **Violation Type**: Type of violation (Speeding, Parking Violation, etc.)
- **Status**: Current status of the violation record (Added as a new field)
  - `Recorded`: Initial violation record
  - `Processed`: Violation has been reviewed and action taken
  - `Cancelled`: Violation record that was dismissed

### From violation_record
- **Zone**: Traffic zone where violation occurred
- **Evidence**: Reference to photo evidence
- **Officer**: Officer who recorded the violation
- **Notes**: Additional details about the violation
- **Speed Limit/Recorded Speed**: For speeding violations

### From violations
- **Name**: Driver/owner name
- **Action Taken**: Enforcement action (Warning/Fine)
- **Frequency**: Number of times this violation has occurred
- **Notified**: Whether owner has been notified
- **Notification Date**: When notification was sent

## Benefits of the Combined Structure

1. **Complete Violation Lifecycle**: Track violations from initial recording through processing and notification
2. **Reduced Redundancy**: No need to duplicate information across collections
3. **Simplified Queries**: All violation data available in one place
4. **Workflow Status Tracking**: The added `Status` field allows tracking each violation through its lifecycle

## Schema and Indexes

The schema for this collection is defined in `combined_violations_schema.json` with the following recommended indexes:
- `License Plate` + `Violation Date` (unique compound index)
- `License Plate` (for queries by vehicle)
- `Violation Date` (for time-based queries)
- `Status` (for status filtering)
- `Violation Type` (for violation type filtering)

## Using the Combined Dataset

### For Display in the UI
```javascript
// Example query to get all processed violations for a vehicle
db.combined_violations.find({
  "License Plate": "MH12BG9876", 
  "Status": "Processed"
})
```

### For Processing Workflow
```javascript
// Example of updating a record from Recorded to Processed
db.combined_violations.updateOne(
  { "_id": ObjectId("1") },
  { 
    $set: { 
      "Status": "Processed",
      "Action Taken": "Warning Issued",
      "Frequency": 1,
      "Notified": true,
      "Notification Date": new Date()
    } 
  }
)
```

## Migration Notes

This combined dataset was created by:
1. Taking all records from both `violation_record` and `violations`
2. Matching records based on License Plate and Violation Date
3. Merging matching records, with `violations` data taking precedence for overlapping fields
4. Adding a `Status` field to track the violation lifecycle

## Integration with Existing Code

To update your application to use this combined structure:
1. Update API endpoints to read/write to the combined collection
2. Modify the management interface to display the status and other merged fields
3. Update your processing workflow to update the status field rather than moving records between collections

By using this combined structure, your application will have a more streamlined data model while maintaining all the functionality of the previous separate collections. 