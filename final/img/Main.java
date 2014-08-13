
import com.google.gdata.data.spreadsheet.ListEntry;
import com.google.gdata.data.spreadsheet.ListFeed;
import org.json.JSONObject;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Element;
import utils.InsertRowIntoSpreadSheet;

import javax.mail.*;
import javax.mail.internet.InternetAddress;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Properties;
import java.util.regex.Pattern;

/**
 * Created by rahulserver on 8/2/14.
 */
public class Main {

    static String googleId = "googlealerts-noreply@google.com";
    static int index = 0;
    static String API_URL = "http://kiarash.scripts.mit.edu/blockedonline_debug/news";

    public static void main(String[] args) {
        String username = args[0];
        String password = args[1];
        //String spreadsheet_title = "GMailScrape123456";
        String spreadsheet_title = args[2];
        //Perform gmail scraping. This will append necessary rows to the Google Spreadsheet.
        scrapeGmail(username, password, spreadsheet_title);
        //Send rows marked with "Accepted" to the server
        makeHttpPost(username, password, spreadsheet_title);
    }

    /**
     * This method scrapes the gmail account for emails from google news alerts.
     * Mails from last 24 hours are fetched and matched for the criteria that
     * they are from the sender googlealerts-noreply@google.com and unread. The
     * mails are then scraped for the details and rows are appended to the
     * google spreadsheet.
     *
     * @param username The full username of gmail account e.g. abc@gmail.com
     * @param password The password
     * @param spreadsheet_title The name of spreadsheet. Its assumed unique in
     * your google drive
     */
    private static void scrapeGmail(String username, String password, String spreadsheet_title) {
        try {
            //Gettin today's date in dd-MMM-yyyy format
            Date cur = new Date();
            DateFormat df = new SimpleDateFormat("dd-MMM-yyyy");
            String curDateString = df.format(cur);
            System.out.println("CurdateString: " + curDateString);
            //Getting the past 24 hours unread google news alert messages 
            //represented by AbstractMessage as it "abstracts" their required fields.
            ArrayList<AbstractMessage> aMsgs = readGmailInboxAndGetAbstractMessagesOfConcern(username, password, 100);
            //For each message
            for (AbstractMessage ams : aMsgs) {
                //Make entries to spreadsheet
                boolean val = InsertRowIntoSpreadSheet.insertNewRowToSpreadsheet(username, password, spreadsheet_title, curDateString,
                        ams.getTitle(), ams.getAgency(), ams.getMessage(), ams.getUrl(), ams.getFlagUrl(), "Pending");
                if (val) {
                    System.out.println("Entered successfully!!");
                } else {
                    System.out.println("Could not be entered!!");
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * This function returns an ArrayList of AbstractMessage matching the
     * criteria that they are from past 24 hrs and are from google news alerts
     * and are unread. Mostly it should return 1 element in the List
     *
     * @param username The username of your gmail account
     * @param password The password of your gmail account
     * @param lastHistory No. of last emails to check for. In case if any mail
     * is found which is older than 24 hrs, loop breaks
     * @return ArrayList of AbstractMessage matching above criteria.
     */
    private static ArrayList<AbstractMessage> readGmailInboxAndGetAbstractMessagesOfConcern(String username, String password, int lastHistory) {
        //initialize mail properties for javamail params.
        Properties props = new Properties();
        //using imap protocol for getting inbox.
        props.setProperty("mail.store.protocol", "imaps");
        //Declaring aMsgs which will be returned to the calling function
        ArrayList<AbstractMessage> aMsgs = new ArrayList<AbstractMessage>();
        try {
            //Getting session object from initialized javamail params
            Session session = Session.getInstance(props, null);
            //Get store object from session
            Store store = session.getStore();
            //Connecting to gmail inbox
            store.connect("imap.gmail.com", username, password);
            //Get inbox from store
            Folder inbox = store.getFolder("INBOX");
            //Open in READ_WRITE so that we are able to mark fetched email which matches our criteria as read
            inbox.open(Folder.READ_WRITE);
            //Getting messages in chronological(older first) order. 
            Message msgs[] = inbox.getMessages(inbox.getMessageCount() - lastHistory, inbox.getMessageCount());
            //For debugging
            System.out.println("MSgs.length " + msgs.length);
            ArrayList<Message> aList = new ArrayList<Message>();
            //Date object representing time 24 hrs ago from now
            Date date = new Date();
            long twentyFourHours = 24 * 60 * 60 * 1000;
            Date yesterday = new Date(date.getTime() - twentyFourHours);
            //Iterating thru the messages of inbox. Reverse order iteration so that we get messages in revers chronological order
            for (int i = msgs.length - 1; i >= 0; i--) {
                Message msg = msgs[i];
                Address[] in = msg.getFrom();
                String sender = InternetAddress.toString(in);
                String msgSubj=msg.getSubject();
                System.out.println((++index) + "SEnder: " + sender);
                //Checking if message is unread
                boolean read = msg.isSet(Flags.Flag.SEEN);
                //If unread and is from the google news alert id, then add to aList
                if (sender.contains(googleId) && !read ) {
                    aList.add(msg);
                }
                //If message has sent date before yesterday, break loop because rest 
                //of the messgaes would be now of time before yesterday as we iterate in reverse chronological order. 
                if (msg.getSentDate().before(yesterday)) {
                    break;
                }
            }
            int c = 0;
            System.out.println("ALIST: " + aList.size());
            //Iteerate thru each element which was matched. Then scrape off its contents and put entry in Google Spreadsheet.
            for (Message m : aList) {
                System.out.println("BErofer");
                //Get content of email
                Object content = m.getContent();
                System.out.println("AFter: " + content.toString());
                if (content instanceof Multipart) {
                    Multipart mp = (Multipart) content;
                    for (int i = 0; i < mp.getCount(); i++) {
                        BodyPart bp = mp.getBodyPart(i);
                        if (Pattern
                                .compile(Pattern.quote("text/html"),
                                        Pattern.CASE_INSENSITIVE)
                                .matcher(bp.getContentType()).find()) {
                            // found html part
                            String html = (String) bp.getContent();
                            Element element = Jsoup.parse(html);
                            List<Element> anchors = element.getElementsByTag("a");
                            //Web scraping it
                            for (Element e : anchors) {
                                try {
                                    if (e.attr("href").startsWith("https://www.google.com/url?rct=j&sa=t&url=")
                                            && !e.attr("style").equalsIgnoreCase("text-decoration:none") && e.parent().tagName().equalsIgnoreCase("span")) {
                                        String url = e.attr("href");
                                        String title = e.text();
                                        String agency = e.parent().parent().child(1).child(0).child(0).text();
                                        String message = e.parent().parent().child(1).child(0).child(1).text();
                                        String flagUrl = "";
                                        try {
                                            List<Element> anchrs = e.parent().parent().select("a[href]");
                                            for (Element a : anchrs) {
                                                if (a.text().trim().equalsIgnoreCase("flag as irrelevant")) {
                                                    flagUrl = a.attr("href");
                                                    break;
                                                }
                                            }
                                        } catch (Exception ex) {
                                            ex.printStackTrace();
                                        }
                                        System.out.println("COUNT: " + (++c));
                                        System.out.println("URL: " + url);
                                        System.out.println("Title: " + title);
                                        System.out.println("agency: " + agency);
                                        System.out.println("Message: " + message);
                                        System.out.println("flagURL: " + flagUrl);
                                        //Construct AbstractMessgefrom it and then add to output list aMsgs
                                        AbstractMessage ams = new AbstractMessage(url, title, agency, message, flagUrl);
                                        aMsgs.add(ams);
                                    }
                                } catch (Exception exc) {
                                    exc.printStackTrace();
                                }
                            }
                        }
                    }
                }
            }
            System.out.println("Total: " + c);
        } catch (Exception mex) {
            mex.printStackTrace();
        }
        return aMsgs;
    }

    /**
     * This function makes http post to server with params as expected by the
     * API_URL
     *
     * @param username The username of gmail id containing the spreadsheet to
     * read data from
     * @param password The password of gmail id containing the spreadsheet to
     * read data from
     * @param spreadsheet_title The "unique" title of spreadsheet. May cause
     * ambiguity or produce unexpected results if its not unique
     */
    private static void makeHttpPost(String username, String password, String spreadsheet_title) {
        try {
            int count = 2;
            //Getting all rows from spreadsheet.
            ListFeed r = InsertRowIntoSpreadSheet.getRowsFromSpreadsheet(username, password, spreadsheet_title);
            List<ListEntry> entries = r.getEntries();
            //Iterating through each rows
            for (ListEntry entry : entries) {
                String flagUrl = entry.getCustomElements().getValue("flagurl");
                String status = entry.getCustomElements().getValue("status");
                //Do Http Get To flagURL
                try {
                    Connection.Response resp = Jsoup.connect(flagUrl).method(Connection.Method.GET).execute();
                    System.out.println("FlagURLstatusCode: " + resp.statusCode());
                } catch (Exception e) {
                    e.printStackTrace();
                }
                //If row's column named 'status' is marked as accepted then do post
                if (status.equalsIgnoreCase("accepted")) {
                    JSONObject json = new JSONObject();
                    String country = entry.getCustomElements().getValue("country");
                    String url = entry.getCustomElements().getValue("url");
                    String date = entry.getCustomElements().getValue("date");
                    String newsTitle = entry.getCustomElements().getValue("newstitle");
                    String newsAgency = entry.getCustomElements().getValue("newsagency");
                    String newsMessage = entry.getCustomElements().getValue("newsmessage");
                    String newsUrl = entry.getCustomElements().getValue("newsurl");

                    json.put("date", new SimpleDateFormat("dd-MMM-yyyy").format(new Date()));
                    json.put("link_to_news", (newsUrl == null) ? "" : newsUrl);
                    json.put("title", (newsTitle == null) ? "" : newsTitle);
                    json.put("description", (newsMessage == null) ? "" : newsMessage);
                    json.put("agency", (newsAgency == null) ? "" : newsAgency);
                    json.put("date_published", (date == null) ? "" : date);
                    json.put("country", (country == null) ? "" : country);
                    json.put("url", (url == null) ? "" : country);
                    //Making http post
                    Connection.Response response = Jsoup.connect(API_URL)
                            .method(Connection.Method.POST)
                            .data("date", json.get("date").toString())
                            .data("link_to_news", (newsUrl == null) ? "" : newsUrl)
                            .data("title", (newsTitle == null) ? "" : newsTitle)
                            .data("description", (newsMessage == null) ? "" : newsMessage)
                            .data("agency", (newsAgency == null) ? "" : newsAgency)
                            .data("date_published", (date == null) ? "" : date)
                            .data("country", (country == null) ? "" : country)
                            .data("url", (url == null) ? "" : url).execute();

                    System.out.println("Status Code JSOUP: " + response.statusCode());
                    //If response code is 200, i.e. post was successful, mark col 'status' as "Sent To Server"
                    if (response.statusCode() == 200) {
                        InsertRowIntoSpreadSheet.updateRowInSpreadsheet(username, password, spreadsheet_title, "Sent To Server", "I" + count);
                    }

                }
                count++;
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

/**
 * This class abstracts out the needed fields from scraped google news email.
 * Fields are self explanatory.
 *
 * @author rahulserver
 */
class AbstractMessage {

    String url;
    String title;
    String agency;
    String message;
    String flagUrl;

    AbstractMessage(String url, String title, String agency, String message, String flagUrl) {
        this.url = url;
        this.title = title;
        this.agency = agency;
        this.message = message;
        this.flagUrl = flagUrl;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getAgency() {
        return agency;
    }

    public void setAgency(String agency) {
        this.agency = agency;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getFlagUrl() {
        return flagUrl;
    }

    public void setFlagUrl(String flagUrl) {
        this.flagUrl = flagUrl;
    }
}
